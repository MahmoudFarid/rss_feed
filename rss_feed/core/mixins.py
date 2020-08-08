
class MultipleSerializerMixin:
    def get_serializer_class(self):
        return self.action_serializer_classes.get(self.action, self.action_serializer_classes.get('default'))
