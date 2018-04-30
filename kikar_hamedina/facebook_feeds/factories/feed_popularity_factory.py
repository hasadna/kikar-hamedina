from django.utils import timezone
import factory
from facebook_feeds.factories.facebook_feed_factory import FacebookFeedFactory
from facebook_feeds import models


class FeedPopularityFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Feed_Popularity

    feed = factory.SubFactory(FacebookFeedFactory)
    date_of_creation = timezone.now()
    fan_count = 100
