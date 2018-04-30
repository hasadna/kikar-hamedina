from django.conf import settings
from django.utils import timezone
from facebook_feeds.factories import FacebookPersonaFactory, \
    FeedPopularityFactory, FacebookFeedFactory, FacebookStatusFactory
from mks.factories import KnessetFactory, PartyFactory, MemberFactory

DEFAULT_NUM_OF_STATUSES = 10
DEFAULT_NUM_OF_POPULARITY_SAMPLES = 10


class CurrentMemberWithFeedFactory(object):
    def __init__(self):
        self.knesset = KnessetFactory.create(
            number=settings.CURRENT_KNESSET_NUMBER)
        self.party = PartyFactory(knesset=self.knesset)
        self.member = MemberFactory(current_party=self.party)
        self.persona = FacebookPersonaFactory(object_id=self.member.id)
        self.member.persona.add(self.persona)
        self.feed = FacebookFeedFactory(persona=self.persona)
        self.persona.main_feed = self.feed.id

        self.member.save()
        self.persona.save()

        self.statuses = []
        self.feed_popularity_samples = []

    def create_facebook_statuses(self, num=DEFAULT_NUM_OF_STATUSES):
        for n in range(num):
            creation_date = timezone.now() - timezone.timedelta(days=n)
            status = FacebookStatusFactory.create(feed=self.feed,
                                                  published=creation_date)
            self.statuses.append(status)

    def create_feed_popularity(self, num=DEFAULT_NUM_OF_POPULARITY_SAMPLES):
        for likes, days_back in zip(range(num), reversed(range(num))):
            creation_date = timezone.now() - timezone.timedelta(days=days_back)
            popularity = FeedPopularityFactory(
                feed=self.feed,
                date_of_creation=creation_date,
                fan_count=likes)
            self.feed_popularity_samples.append(popularity)
