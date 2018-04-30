from django.core.urlresolvers import reverse
from django.test import TestCase

from facebook_feeds.models import Facebook_Feed, Facebook_Persona, \
    Facebook_Status, Feed_Popularity

from mks.models import Knesset, Member, Party
from core.tests.composite_factories import CurrentMemberWithFeedFactory


def format_status_id(facebook_feed, status_id):
    return "{}_{}".format(facebook_feed.id, status_id)


class CoreViewsTests(TestCase):
    def setUp(self):
        member_composite = CurrentMemberWithFeedFactory()
        self.member = member_composite.member
        member_composite.create_facebook_statuses()
        member_composite.create_feed_popularity()

    def tearDown(self):
        Knesset.objects.all().delete()
        Party.objects.all().delete()
        Member.objects.all().delete()
        Feed_Popularity.objects.all().delete()
        Facebook_Feed.objects.all().delete()
        Facebook_Status.objects.all().delete()
        Facebook_Persona.objects.all().delete()

    def test_about_us(self):
        url = reverse("about")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_homepage(self):
        url = reverse("index")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_member(self):
        url = reverse("member", args=[self.member.id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_party(self):
        url = reverse("party", args=[self.member.current_party_id])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_get_search_page(self):
        url = reverse("search")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
