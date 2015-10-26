from collections import OrderedDict

from .ld import ROOT_NAMESPACE

PERM_TO_HYDRA_TYPE = {
    'add': 'hydra:CreateResourceOperation',
    'change': 'hydra:ReplaceResourceOperation',
    'delete': 'hydra:DeleteResourceOperation'
}

PERM_TO_HYDRA_TITLE = {
    'add': 'Create a new {}',
    'change': 'Replace an existing {}',
    'delete': 'Delete an existing {}'
}

PERM_TO_METHOD = {
    'add': 'POST',
    'change': 'PUT',
    'delete': 'DELETE'
}


def operation_from_perm(user, project, perm_label):
    codename = perm_label.split('.')[1]
    perm_type = codename.split('_')[0]
    assert perm_type in ['add', 'change', 'delete'], (
        'Hydra operations only supported for add, change, and '
        'delete permissions.'
    )

    has_perm = (
        user.is_authenticated() and
        user.has_project_perm(project, perm_label)
    )

    if not has_perm:
        return None

    perm, = filter(lambda perm: perm.codename == codename,
                   user.get_project_permission_objects(project))

    model_opts = perm.content_type.model_class()._meta

    hydra_type = PERM_TO_HYDRA_TYPE[perm_type]
    hydra_title = PERM_TO_HYDRA_TITLE[perm_type]
    method = PERM_TO_METHOD[perm_type]

    return OrderedDict((
        ('@type', hydra_type),
        ('label', hydra_title.format(model_opts.verbose_name)),
        ('description', None),
        ('hydra:method', method),
        ('hydra:expects', ROOT_NAMESPACE + model_opts.object_name),
        ('hydra:returns', ROOT_NAMESPACE + model_opts.object_name),
        ('hydra:possibleStatus', [])
    ))


def project_links_for_request_user(project, request):
    user = request.user

    add_perms = user._get_project_role(project)\
        .get_permissions()\
        .filter(codename__in=('add_note', 'add_topic', 'add_document'))

    available_add_perms_by_model = {
        perm.codename.split('_')[1]: ['main.' + perm.codename]
        for perm in add_perms
    }

    project_url = request.build_absolute_uri(project.get_absolute_url())

    return [
        OrderedDict((
            ('@id', '{}doc/#{}s'.format(project_url, model)),
            ('@type', 'hydra:Link'),
            ('hydra:title', '{} list'.format(model.title())),
            ('hydra:supportedOperation', [
                operation_from_perm(user, project, codename)
                for codename in available_add_perms_by_model.get(model, [])
            ])
        ))
        for model in ('note', 'topic', 'document')
    ]
