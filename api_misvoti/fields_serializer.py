from rest_framework import serializers


class PlanEstudioCreadoUrl(serializers.HyperlinkedIdentityField):
    def __init__(self, view_name=None, **kwargs):
        self.lookup_fields = kwargs.pop('lookup_fields', None)
        super(PlanEstudioCreadoUrl, self).__init__(view_name, **kwargs)

    def get_object(self, view_name, view_args, view_kwargs):
        print "PlanEstudioCreadoUrl(" + str(self) + ").get_object"
        return super(PlanEstudioCreadoUrl, self).get_object(view_name, view_args, view_kwargs)

    def get_url(self, obj, view_name, request, format):
        #print "PlanEstudioCreadoUrl(" + str(self) + ").get_url", obj, view_name, request, format

        if not self.lookup_fields:
            return super(PlanEstudioCreadoUrl, self).get_url(obj, view_name, request, format)
        else:
            # Unsaved objects will not yet have a valid URL.
            if hasattr(obj, 'pk') and obj.pk in (None, ''):
                return None

            fields = {}
            for name, attrs in self.lookup_fields.items():
                value = obj
                for attr in attrs.split('.'):
                    try:
                        value = getattr(value, attr)
                    except AttributeError:
                        value = attr
                fields[name] = value

            print fields

            return self.reverse(view_name, kwargs=fields, request=request, format=format)

