# coding=utf-8
from django.utils import timezone
import factory
from facebook_feeds import models

TEXT_IN_HEBREW = u"""
 בה תרבות צילום קהילה כדי, דת ציור כניסה עזה. ביולי רומנית 
    לעריכה זכר מה, מתוך הארץ מיזמים ויש אם, זכר אל קולנוע אינטרנט 
    האנציקלופדיה. גם לערכים לימודים בקר. מלא כימיה ננקטת לחיבור אל, 
    מה בחירות הקהילה תאולוגיה אנא, מה תנך ננקטת מונחים גרמנית. 

מתוך תקשורת סוציולוגיה של אנא. מפתח למנוע ערבית אחר של, הראשי בהשחתה כלל על, 
תנך אל טיפול כלשהו אגרונומיה. ערכים משופרות האטמוספירה שמו אל. בדף גם הנדסת 
הבאים משפטית, אל הטבע תורת ראשי צעד. אחד אחרים אחרונים מה, של מלא מתוך 
אגרונומיה. צ'ט את אינו וספציפיים, בקר אם ניהול לערכים וכמקובל. גם אתה יכול 
המשפט משחקים. 
"""


def format_status_id(instance, seq):
    return "{}_{}".format(instance.feed.id, seq)


class FacebookStatusFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Facebook_Status

    feed = factory.SubFactory(models.Facebook_Feed)
    content = TEXT_IN_HEBREW
    status_id = factory.LazyAttributeSequence(format_status_id)
    published = timezone.now()
    updated = timezone.now()
    locally_updated = timezone.now()
    is_comment = False
    is_deleted = False
