from rest_framework.serializers import ValidationError

class UniqueToProjectValidator:
    message = u'{model_name} with this {field_name} already exists.'
    def __init__(self, field, message=None):
        self.field_name = field
        self.message = message or self.message
    def set_context(self, serializer):
        self.ModelClass = serializer.Meta.model
        self.instance = getattr(serializer, 'instance', None)
    def __call__(self, attrs):
        # Assuming that the field is always required
        if self.instance is not None:
            value = attrs.get(self.field_name,
                              getattr(self.instance, self.field_name))
        else:
            value = attrs[self.field_name]

        kwargs = { 'project': attrs['project'], self.field_name: value}
        qs = self.ModelClass.objects.filter(**kwargs)
        if self.instance is not None:
            qs = qs.exclude(id=self.instance.id)

        if qs.exists():
            opts = self.ModelClass._meta
            raise ValidationError({
                self.field_name: self.message.format(
                    model_name=opts.verbose_name.title(),
                    field_name=opts.get_field(self.field_name).verbose_name
                )
            })
