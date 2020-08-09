from rest_framework import serializers

from .models import Feed, Item
from .utils import parse_rss_link
from .validators import validate_rss_link


class FeedSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Feed
        fields = ('id', 'created_by', 'title', 'xml_url', 'link', 'description', 'image', 'is_followed', 'last_update')
        extra_kwargs = {
            'title': {"required": False},
            'link': {"required": False},
            'description': {"required": False},
            'image': {"required": False},
            'is_followed': {"read_only": True},
        }

    def validate(self, validate_data):
        xml_url = validate_data.get('xml_url')
        parsed = parse_rss_link(xml_url)
        error = validate_rss_link(parsed)
        if error:
            raise serializers.ValidationError({"non_field_errors": error})
        validate_data['parsed'] = parsed
        return validate_data


class ItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = Item
        fields = ('id', 'feed', 'title', 'link', 'published_time', 'description', 'last_update')


class ItemStateSerializer(serializers.ModelSerializer):
    ids = serializers.ListField(allow_empty=False)

    class Meta:
        model = Item
        fields = ('ids',)

    def validate_ids(self, ids):
        if len(ids) != Item.objects.filter(id__in=ids, state=Item.STATE_CHOICES.UNREAD).count():
            raise serializers.ValidationError("Some ids not found or its state is not correct")
        return ids
