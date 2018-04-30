from django.utils import timezone
import factory

from facebook_feeds import models
from facebook_feeds.factories.facebook_persona_factory import FacebookPersonaFactory

FACEBOOK_URL = "https://www.facebook.com/"


class FacebookFeedFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Facebook_Feed

    persona = factory.SubFactory(
        FacebookPersonaFactory,
        main_feed=factory.LazyAttribute(lambda x: x.id))
    vendor_id = factory.Sequence(lambda n: n)
    name = factory.Sequence(lambda n: "feed {}".format(n))
    username = factory.Sequence(lambda n: "username {}".format(n))
    birthday = None
    link = factory.LazyAttribute(lambda x: FACEBOOK_URL + x.username + "/")
    is_current = True
    feed_type = 'PP'
    picture_large = None
    picture_square = None
    requires_user_token = False
    current_fan_count = 0
    locally_updated = factory.LazyFunction(timezone.now)
