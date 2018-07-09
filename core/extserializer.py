from django.core.serializers.json import Serializer as JsonSerializer
from django.core.serializers.python import Serializer as PythonSerializer
from django.core.serializers.base import Serializer as BaseSerializer

class ExtBaseSerializer(BaseSerializer):

    # def start_serialization(self):
    #     super().start_serialization()
    #
    # def start_object(self, obj):
    #     super().start_object(obj)

    def serialize(self, queryset, **options):
        self.selected_props = options.pop('props')
        return super(ExtBaseSerializer, self).serialize(queryset, **options)

    def serialize_property(self, obj):
        model = type(obj)
        for field in self.selected_props:
            if hasattr(model, field) and type(getattr(model, field)) == property:
                self.handle_prop(obj, field)

    def handle_prop(self, obj, field):
        self._current[field] = getattr(obj, field)

    def end_object(self, obj):
        self.serialize_property(obj)

        super(ExtBaseSerializer, self).end_object(obj)

class ExtPythonSerializer(ExtBaseSerializer, PythonSerializer):
    pass

class ExtJsonSerializer(ExtPythonSerializer, JsonSerializer):
    pass


# class ExtSerializer(BaseSerializer):
#
#
#
#     def start_object(self, obj):
#         pass
#
#     def handle_field(self, obj, field):
#         pass
#
#     def start_serialization(self):
#         super()
#
#     def serialize_property(self, obj):
#         model = type(obj)
#         for field in self.selected_fields:
#             if hasattr(model, field) and type(getattr(model, field)) == property:
#                 self.handle_prop(obj, field)
#
#     def handle_prop(self, obj, field):
#         self._current[field] = getattr(obj, field)
#
#     def end_object(self, obj):
#         self.serialize_property(obj)
#
#         super(ExtBaseSerializer, self).end_object(obj)
#
#
# class ExtPythonSerializer(ExtBaseSerializer, PythonSerializer):
#     pass
#
#
# class ExtJsonSerializer(ExtPythonSerializer, JsonSerializer):
#     pass