from django.conf.urls import url, include
from django.conf.urls.static import static
from rest_framework.urlpatterns import format_suffix_patterns
from solid_i18n.urls import solid_i18n_patterns as patterns

from core.api import PersonaResource
from core.sitemap import MkSitemap, PartySitemap, StaticViewSitemap
from . import views
from facebook_feeds.models import Facebook_Status, TAG_NAME_CHARSET
from kikartags.models import Tag as Tag
from mks.models import Party
from django.conf import settings
from tastypie.api import Api
from api import MemberResource, PartyResource, KnessetResource, \
    Facebook_StatusResource, \
    Facebook_Status_CommentResource, Facebook_FeedResource, TagResource, \
    CommentTagResource
from insights import StatsMemberResource, StatsPartyResource
from core.rss_feeds import LatestStatusesRSSFeed, PartyRSSFeed, \
    MemberRSSFeed, KeywordsByUserRSSFeed, CustomQueryRSSFeed
from django.contrib.sitemaps.views import sitemap

v1_api = Api(api_name='v1')
v1_api.register(MemberResource())
v1_api.register(PartyResource())
v1_api.register(KnessetResource())
v1_api.register(Facebook_StatusResource())
v1_api.register(Facebook_Status_CommentResource())
v1_api.register(Facebook_FeedResource())
v1_api.register(PersonaResource())
v1_api.register(TagResource())
v1_api.register(CommentTagResource())
v1_api.register(StatsMemberResource())
v1_api.register(StatsPartyResource())

sitemaps = {
    'mk': MkSitemap,
    'party': PartySitemap,
    'static': StaticViewSitemap
}

urlpatterns = patterns('',
                       # homepage
                       url(r'^$', views.AllStatusesView.as_view(),
                           name='index'),
                       # include urls
                       url(r'^api/', include(v1_api.urls)),
                       url(r'^comments/', include('django_comments.urls')),
                       url(r'^billboards/$', views.BillboardsView.as_view(),
                           name='billboards'),
                       # TODO: rename to `hot` to covr hot topics
                       url(r'^hot-topics/$', views.HotTopicsView.as_view(),
                           name='hot-topics'),
                       url(r'^searchgui/$', views.SearchGuiView.as_view(),
                           name="search-gui"),
                       url(r'^about/$', views.AboutUsView.as_view(),
                           name='about', ),
                       url(r'^all-statuses/$',
                           views.AllStatusesView.as_view(),
                           kwargs={'context_object': 'index'},
                           name='all-statuses'),
                       url(r'^search_bar/$', views.search_bar),
                       # main status filter-views in website
                       url(r'^party/(?P<id>\d+)/$', views.PartyView.as_view(),
                           kwargs={
                               'variable_column': 'feed__person__party__id',
                               'context_object': 'party'},
                           name='party'),
                       url(r'^member/(?P<id>\d+)/$',
                           views.MemberView.as_view(),
                           kwargs={
                               'variable_column': 'feed__persona__object_id',
                               'context_object': 'member'},
                           name='member'),
                       url(
                           r'^tag/(?P<search_field>\w+)/(?P<id>%s+)/$' %
                           TAG_NAME_CHARSET,
                           views.TagView.as_view(),
                           kwargs={'variable_column': 'tags',
                                   'context_object': 'tag'},
                           name='tag'),
                       url(r'^search/$', views.SearchView.as_view(),
                           kwargs={'variable_column': 'content',
                                   'context_object': 'search'}, name='search'),
                       url(r'^preview/$', views.SearchPreviewView.as_view(),
                           kwargs={'variable_column': 'content',
                                   'context_object': 'search'},
                           name='preview'),
                       url(r'^customs/(?P<username>\w+)/$',
                           views.CustomsByUserView.as_view(),
                           name='customs-by-user'),
                       url(r'^customs/$', views.AllCustomsView.as_view(),
                           name='all-customs'),
                       url(r'^custom/save/$', views.save_queryset_for_user,
                           name='save-custom-request'),
                       url(r'^custom/delete/$', views.delete_queryset,
                           name='delete-custom-request'),
                       url(r'^custom/id/(?P<id>\d+)/$',
                           views.CustomViewByID.as_view(),
                           name='custom-by-id'),
                       url(r'^custom/(?P<title>[\w\d\.\s-]+)/$',
                           views.CustomView.as_view(), name='custom'),
                       url(r'^title_exists/', views.title_exists,
                           name='title-exists'),
                       # Views for all objects of type
                       url(r'^members/$', views.AllMembers.as_view(
                           queryset=Party.objects.filter(
                               knesset__number=settings.
                               CURRENT_KNESSET_NUMBER)),
                           name='all-members'),
                       url(r'^parties/$', views.AllParties.as_view(
                           queryset=Party.objects.filter(
                               knesset__number=settings.
                               CURRENT_KNESSET_NUMBER)),
                           name='all-parties'),
                       url(r'^tags/$',
                           views.AllTags.as_view(queryset=Tag.objects.all()),
                           name='all-tags'),
                       # urls and views used only indirectly
                       url(r'^status_permalink/(?P<slug>[-_\w]+)/$',
                           views.FacebookStatusDetailView.as_view(),
                           name='status-detail'),
                       url(r'^fblogin/$', views.login_page, name='fblogin'),
                       url(r'^fblogin/get-data/$',
                           views.get_data_from_facebook,
                           name='get-data-from-facebook'),
                       url(r'^status_update/(?P<status_id>\w+)/$',
                           views.status_update),
                       url(r'^add_tag_to_status/$', views.add_tag_to_status),
                       # unused Views for statuses
                       url(r'^status-comments/$',
                           views.OnlyCommentsView.as_view(),
                           name='status-comments'),
                       url(r'^untagged/$',
                           views.AllStatusesView.as_view(
                               queryset=Facebook_Status.objects.filter(
                                   tags=None,
                                   feed__persona__object_id__isnull=False).
                               order_by('-published')),
                           kwargs={'context_object': 'untagged'},
                           name='untagged'),
                       url(r'^review-tags/$', views.ReviewTagsView.as_view(),
                           name='review-tags'),
                       # rss feeds
                       url(r'^latest/feed/$', LatestStatusesRSSFeed(),
                           name='rss-feed-latest'),
                       url(r'^party/(?P<party_id>\d+)/rss/$', PartyRSSFeed()),
                       url(r'^member/(?P<member_id>\d+)/rss/$',
                           MemberRSSFeed()),
                       url(r'^user/(?P<user_id>\d+)/rss/$',
                           KeywordsByUserRSSFeed()),
                       url(r'^custom/(?P<title>[\w\d\.\s-]+)/rss/$',
                           CustomQueryRSSFeed(), name='custom-query-rss'),
                       url(r'^custom/(?P<title>[\w\d\.\s-]+)/rss/widget/$',
                           views.CustomWidgetView.as_view(),
                           name='custom-query-rss-widget'),
                       url(r'^latest/widget/$', views.WidgetView.as_view(),
                           name='rss-widget-latest'),
                       url(r'^suggested_tags/(?P<status_id>[-_\w]+)/$',
                           views.return_suggested_tags),
                       url(r'^sitemap\.xml/$', sitemap, {'sitemaps': sitemaps},
                           name='django.contrib.sitemaps.views.sitemap'),
                       ) + static(settings.MEDIA_URL,
                                  document_root=settings.MEDIA_ROOT)

urlpatterns = format_suffix_patterns(urlpatterns)
