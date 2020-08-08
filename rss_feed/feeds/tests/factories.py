import factory

from rss_feed.users.tests.factories import UserFactory

from ..models import Feed, Item


class FeedFactory(factory.DjangoModelFactory):
    class Meta:
        model = Feed

    created_by = factory.SubFactory(UserFactory)
    title = factory.Faker("name")
    description = factory.Faker("sentence", nb_words=5)
    link = factory.Faker("url")
    xml_url = factory.Faker('url')
    is_followed = factory.Faker('pybool')


class ItemFactory(factory.DjangoModelFactory):
    class Meta:
        model = Item

    feed = factory.SubFactory(FeedFactory)
    title = factory.Faker("sentence", nb_words=5)
    description = factory.Faker("sentence", nb_words=5)
    state = factory.Faker("random_element", elements=Item.STATE_CHOICES._db_values)
    link = factory.Faker("url")
