import re

from django.conf import settings
from django.utils import timezone

from facebook_feeds.models import Facebook_Status

# current knesset number
MAX_UNTAGGED_POSTS = 1000
CURRENT_KNESSET_NUMBER = getattr(settings, 'CURRENT_KNESSET_NUMBER', 19)

# Elections mode (use candidates instead of MKs)
IS_ELECTIONS_MODE = getattr(settings, 'IS_ELECTIONS_MODE', False)

# used for calculating top gainer of fan_count
MIN_FAN_COUNT_FOR_REL_COMPARISON = getattr(settings,
                                           'MIN_FAN_COUNT_FOR_REL_COMPARISON',
                                           5000)
DEFAULT_POPULARITY_DIF_COMPARISON_TYPE = getattr(
    settings, 'DEFAULT_POPULARITY_DIF_COMPARISON_TYPE', 'rel')
POPULARITY_DIF_DAYS_BACK = getattr(settings, 'POPULARITY_DIF_DAYS_BACK', 30)

# search logic default operator
DEFAULT_OPERATOR = getattr(settings, 'DEFAULT_OPERATOR', 'or')

# order by default
DEFAULT_STATUS_ORDER_BY = getattr(settings, 'DEFAULT_STATUS_ORDER_BY',
                                  '-published')
allowed_fields_for_order_by = [field.name for field in
                               Facebook_Status._meta.fields]
ALLOWED_FIELDS_FOR_ORDER_BY = getattr(settings, 'ALLOWED_FIELDS_FOR_ORDER_BY',
                                      allowed_fields_for_order_by)

# filter by date options
FILTER_BY_DATE_DEFAULT_START_DATE = getattr(
    settings, 'FILTER_BY_DATE_DEFAULT_START_DATE',
    timezone.datetime(2000, 1, 1, 0, 0, tzinfo=timezone.utc))

# hot-topics page
NUMBER_OF_LAST_DAYS_FOR_HOT_TAGS = getattr(settings,
                                           'NUMBER_OF_LAST_DAYS_FOR_HOT_TAGS',
                                           7)

# needs_refresh - Constants for quick status refresh
MAX_STATUS_AGE_FOR_REFRESH = getattr(settings, 'MAX_STATUS_AGE_FOR_REFRESH',
                                     60 * 60 * 24 * 2)  # 2 days
MIN_STATUS_REFRESH_INTERVAL = getattr(settings, 'MIN_STATUS_REFRESH_INTERVAL',
                                      5)  # 5 seconds
MAX_STATUS_REFRESH_INTERVAL = getattr(settings, 'MAX_STATUS_REFRESH_INTERVAL',
                                      60 * 10)  # 10 minutes

# Python regex for splitting words
RE_SPLIT_WORD_UNICODE = re.compile('\W+', re.UNICODE)

# Postgres regex for word boundaries. Unfortunately Hebrew support is not
# good, so can't use \W (\W detects Hebrew characters as non-word chars).
# Including built-in punctuation and whitespace plus a unicode range with some
# exotic spaces/dashes/quotes
PG_RE_NON_WORD_CHARS = u'[[:punct:][:space:]\u2000-\u201f]+'
# Start/end of phrase also allow beginning/end of statue
PG_RE_PHRASE_START = u'(^|%s)' % (PG_RE_NON_WORD_CHARS,)
PG_RE_PHRASE_END = u'(%s|$)' % (PG_RE_NON_WORD_CHARS,)

HOURS_SINCE_PUBLICATION_FOR_SIDE_BAR = getattr(
    settings, 'HOURS_SINCE_PUBLICATION_FOR_SIDE_BAR', 3)

NUMBER_OF_WROTE_ON_TOPIC_TO_DISPLAY = getattr(
    settings, 'NUMBER_OF_WROTE_ON_TOPIC_TO_DISPLAY', 3)

NUMBER_OF_TAGS_TO_PRESENT = getattr(settings, 'NUMBER_OF_TAGS_TO_PRESENT', 3)

NUMBER_OF_SUGGESTIONS_IN_SEARCH_BAR = getattr(
    settings, 'NUMBER_OF_SUGGESTIONS_IN_SEARCH_BAR', 3)

MAX_STATUSES_IN_RSS_FEED = getattr(settings, 'MAX_STATUSES_IN_RSS_FEED', 30)

FEED_TIME_TO_LIVE = 15

DEFAULT_DAYS_BACK_RSS = 30

FEATURED_SEARCH_TERM_UNICODE = (
    u'\u05e6\u05d5\u05e0\u05d0\u05de\u05d9')  # Tzunami
FEATURED_SEARCH_TERM_URL_ESCAPE = u'%22%D7%A6%D7%95%D7%A0%D7%90%D7%9E%D7%99%22'
