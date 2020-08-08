from rest_framework import serializers

from .models import Feed, Item
from .validators import validate_rss_link
from .utils import parse_rss_link


class FeedSerializer(serializers.ModelSerializer):
    created_by = serializers.HiddenField(default=serializers.CurrentUserDefault())

    class Meta:
        model = Feed
        fields = ('id', 'created_by', 'title', 'xml_url', 'link', 'description', 'image')
        extra_kwargs = {
            'title': {"required": False},
            'link': {"required": False},
            'description': {"required": False},
            'image': {"required": False},
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
        fields = ('id', 'feed', 'title', 'link', 'published_time', 'description', 'modified')
