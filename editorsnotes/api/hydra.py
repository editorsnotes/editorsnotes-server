from collections import OrderedDict

from .ld import ROOT_NAMESPACE

PERM_TO_HYDRA_TYPE = {
    'add': 'CreateResourceOperation',
    'change': 'ReplaceResourceOperation',
    'delete': 'DeleteResourceOperation'
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

    perm = user._get_project_role(project)\
        .get_permissions()\
        .get(codename=codename)

    model_opts = perm.content_type.model_class()._meta

    hydra_type = PERM_TO_HYDRA_TYPE[perm_type]
    hydra_title = PERM_TO_HYDRA_TITLE[perm_type]
    method = PERM_TO_METHOD[perm_type]

    return OrderedDict((
        ('type', hydra_type),
        ('title', hydra_title.format(model_opts.verbose_name)),
        ('method', method),
        ('expects', ROOT_NAMESPACE + model_opts.object_name),
        ('returns', ROOT_NAMESPACE + model_opts.object_name)
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
            ('url', '{}doc/#{}s'.format(project_url, model)),
            ('type', 'Link'),
            ('title', '{} list'.format(model.title())),
            ('supportedOperation', [
                operation_from_perm(user, project, codename)
                for codename in available_add_perms_by_model.get(model, [])
            ])
        ))
        for model in ('note', 'topic', 'document')
    ]
