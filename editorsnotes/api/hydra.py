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

    perm, = [perm for perm in user.get_project_permission_objects(project) if perm.codename == codename]

    model_opts = perm.content_type.model_class()._meta

    hydra_type = PERM_TO_HYDRA_TYPE[perm_type]
    hydra_title = PERM_TO_HYDRA_TITLE[perm_type]
    method = PERM_TO_METHOD[perm_type]

    return OrderedDict((
        ('@type', hydra_type),
        ('label', hydra_title.format(model_opts.verbose_name)),
        ('description', None),
        ('hydra:method', method),
        ('hydra:expects', { "@id": ROOT_NAMESPACE + model_opts.object_name }),
        ('hydra:returns', { "@id": ROOT_NAMESPACE + model_opts.object_name }),
        ('hydra:possibleStatus', [])
    ))
