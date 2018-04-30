import datetime
import json
import logging
import re
from random import choice

import facebook
import waffle
from django.conf import settings
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.db.models import Count, Q
from django.http import HttpResponseRedirect, HttpResponse, HttpRequest, \
    QueryDict
from django.shortcuts import render, render_to_response, get_object_or_404, \
    redirect
from django.template import RequestContext
from django.utils import timezone
from django.views.decorators.csrf import csrf_protect
from django.views.generic import DetailView, ListView
from endless_pagination.views import AjaxListView
from facebook import GraphAPIError

from core import params
from core.billboards import Billboards
from core.insights import StatsEngine
from core.models import MEMBER_MODEL, PARTY_MODEL, UserSearch
from core.qserializer import QSerializer
from core.query_utils import get_parsed_request, parse_to_q_object, \
    apply_request_params, get_order_by, filter_by_date
from facebook_feeds.management.commands import updatestatus
from facebook_feeds.models import Facebook_Feed, User_Token, Facebook_Status, \
    TAG_NAME_REGEX
from facebook_feeds.models import Tag as OldTag
from kikartags.models import Tag as Tag, HasSynonymError, TaggedItem

logger = logging.getLogger(__file__)


class StatusListView(AjaxListView):
    page_template = "core/facebook_status_list.html"


class AboutUsView(ListView):
    template_name = 'core/about_us.html'
    model = Facebook_Status

    def get_context_data(self, **kwargs):
        context = super(AboutUsView, self).get_context_data(**kwargs)
        new_statuses_last_day = Facebook_Status.objects.filter(published__gte=(
            datetime.date.today() - datetime.timedelta(days=1))).count()
        context['IS_ELECTION_MODE'] = params.IS_ELECTIONS_MODE
        context['statuses_last_day'] = new_statuses_last_day
        members = MEMBER_MODEL.objects.all()
        members_with_persona = [member for member in members if
                                member.facebook_persona and member.is_current]
        members_with_feed = [member for member in members_with_persona if
                             member.facebook_persona.feeds.filter(
                                 feed_type='PP')]
        context['number_of_mks'] = len(members_with_feed)

        party_ids = [x['id'] for x in
                     PARTY_MODEL.current_knesset.all().values('id')]
        try:
            featured_party_id = choice(party_ids)
            context['featured_party'] = PARTY_MODEL.objects.get(
                id=featured_party_id)
        except IndexError:
            context['featured_party'] = PARTY_MODEL.objects.first()

        context['featured_search'] = {
            'search_value': (u'search_str=' +
                             params.FEATURED_SEARCH_TERM_URL_ESCAPE),
            'search_name': params.FEATURED_SEARCH_TERM_UNICODE}
        max_change = (
            Facebook_Feed.current_feeds.get_largest_fan_count_difference(
                params.POPULARITY_DIF_DAYS_BACK,
                params.DEFAULT_POPULARITY_DIF_COMPARISON_TYPE,
                params.MIN_FAN_COUNT_FOR_REL_COMPARISON))
        feed = max_change['feed']
        max_change['member'] = MEMBER_MODEL.objects.get(
            persona=feed.persona)
        context['top_growth'] = max_change
        return context


class HotTopicsView(ListView):
    model = Tag
    template_name = 'core/hot_topics.html'

    def get_queryset(self):

        relevant_statuses = Facebook_Status.objects.filter(published__gte=(
            datetime.date.today() - datetime.timedelta(
                days=params.NUMBER_OF_LAST_DAYS_FOR_HOT_TAGS)))
        status_ids = [status.id for status in relevant_statuses]
        queryset = Tag.objects.filter(
            is_for_main_display=True,
            kikartags_taggeditem_items__object_id__in=status_ids).annotate(
            number_of_posts=Count('kikartags_taggeditem_items')).order_by(
            '-number_of_posts')[:params.NUMBER_OF_TAGS_TO_PRESENT]
        return queryset

    def get_context_data(self, **kwargs):
        context = super(HotTopicsView, self).get_context_data(**kwargs)
        wrote_about_tag = dict()
        for tag in context['object_list']:
            list_of_writers = Facebook_Feed.objects.filter(
                facebook_status__tags__id=tag.id).distinct()
            list_of_writers_with_latest_fan_count = list()
            for feed in list_of_writers:
                list_of_writers_with_latest_fan_count.append(
                    {'feed': feed,
                     'fan_count': feed.current_fan_count})
            sorted_list_of_writers = sorted(
                list_of_writers_with_latest_fan_count,
                key=lambda x: x['fan_count'],
                reverse=True)
            feeds = [feed['feed'] for feed in sorted_list_of_writers]
            wrote_about_tag[tag] = (
                feeds[:params.NUMBER_OF_WROTE_ON_TOPIC_TO_DISPLAY])
        context['wrote_about_tag'] = wrote_about_tag
        return context


class BillboardsView(ListView):
    template_name = 'core/billboards_list.html'
    model = Facebook_Feed

    stats = StatsEngine()

    def get_queryset(self, **kwargs):
        return Facebook_Feed.current_feeds.first()

    def get_context_data(self, **kwargs):
        context = super(BillboardsView, self).get_context_data(**kwargs)

        billboards = Billboards()

        context['list_of_billboards'] = []
        context['list_of_billboards'].append(
            billboards.number_of_followers_board)
        context['list_of_billboards'].append(
            billboards.popularity_growth_board)
        context['list_of_billboards'].append(billboards.number_of_status_board)
        context['list_of_billboards'].append(
            billboards.median_status_likes_board)
        context['list_of_billboards'].append(billboards.top_likes_board)

        context['list_of_billboards'] = sorted(context['list_of_billboards'],
                                               key=lambda x: x[
                                                   'order_of_board'])

        return context


class OnlyCommentsView(StatusListView):
    model = Facebook_Status
    template_name = 'core/homepage_all_statuses.html'

    def get_queryset(self):
        return apply_request_params(
            Facebook_Status.objects_no_filters.filter(is_comment=True),
            self.request)


class AllStatusesView(StatusListView):
    model = Facebook_Status
    template_name = 'core/homepage_all_statuses.html'

    # paginate_by = 100

    def get_queryset(self):
        retset = apply_request_params(
            super(AllStatusesView, self).get_queryset(), self.request)
        # untagged url is known to be super heavy on the DB.
        # That is why it is hard coded limited to MAX_UNTAGGED matches.
        # Agam Rafaeli - 2/1/2015
        if self.request.resolver_match.url_name == "untagged":
            retset = retset[:params.MAX_UNTAGGED_POSTS]
        return retset

    def get_context_data(self, **kwargs):
        context = super(AllStatusesView, self).get_context_data(**kwargs)
        feeds = Facebook_Feed.objects.filter(
            facebook_status__published__gte=(
                datetime.date.today() - datetime.timedelta(
                    hours=params.HOURS_SINCE_PUBLICATION_FOR_SIDE_BAR
                ))).distinct()
        context['side_bar_list'] = MEMBER_MODEL.objects.filter(
            id__in=[feed.persona.owner_id for feed in
                    feeds]).distinct().order_by('name')
        context['side_bar_parameter'] = (
            params.HOURS_SINCE_PUBLICATION_FOR_SIDE_BAR)
        return context


class SearchView(StatusListView):
    model = Facebook_Status
    context_object_name = 'filtered_statuses'
    template_name = "core/search.html"

    def get_queryset(self):
        params_dict = get_parsed_request(get_params=self.request.GET)
        query_Q = parse_to_q_object(self.request.GET, params_dict)
        return apply_request_params(Facebook_Status.objects.filter(query_Q),
                                    self.request)

    def get_context_data(self, **kwargs):
        context = super(SearchView, self).get_context_data(**kwargs)
        params_dict = get_parsed_request(get_params=self.request.GET)
        query_Q = parse_to_q_object(self.request.GET, params_dict)
        context['members'] = MEMBER_MODEL.objects.filter(
            id__in=params_dict['members_ids'])

        context['parties'] = PARTY_MODEL.objects.filter(
            id__in=params_dict['parties_ids'])

        context['tags'] = Tag.objects.filter(id__in=params_dict['tags_ids'])

        context['search_str'] = params_dict['phrases']

        context['excluded'] = Facebook_Status.objects.filter(
            status_id__in=params_dict['excluded'])

        context['search_title'] = ", ".join(
            [x for x in params_dict['phrases']]) or ", ".join(
            x.name for x in context['tags'])

        context['request_arguments'] = self.request. \
            get_full_path().split('?')[-1]

        return_queryset = apply_request_params(
            Facebook_Status.objects.filter(query_Q), self.request)
        context['number_of_results'] = return_queryset.count()
        context['side_bar_parameter'] = (
            params.HOURS_SINCE_PUBLICATION_FOR_SIDE_BAR)

        return context


class SearchPreviewView(SearchView):
    model = Facebook_Status
    context_object_name = 'filtered_statuses'
    template_name = 'core/embedded_container.html'


class SearchGuiView(StatusListView):
    model = Facebook_Status
    template_name = "core/searchgui.html"


class StatusFilterUnifiedView(StatusListView):
    model = Facebook_Status
    context_object_name = 'filtered_statuses'
    page_template = "core/facebook_status_list.html"

    def get_queryset(self):
        variable_column = self.kwargs['variable_column']
        search_string = self.kwargs['id']
        if self.kwargs['context_object'] == 'tag':
            search_field = self.kwargs['search_field']
            if search_field == 'id':
                search_field = 'id'
            else:
                search_field = 'name'
            selected_filter = variable_column + '__' + search_field
        else:
            selected_filter = variable_column

        return apply_request_params(
            Facebook_Status.objects.filter(**{selected_filter: search_string}),
            self.request)

    def get_context_data(self, **kwargs):
        context = super(StatusFilterUnifiedView, self).get_context_data(
            **kwargs)

        object_id = self.kwargs['id']
        search_field = self.kwargs.get('search_field', 'id')
        context['object'] = self.parent_model.objects.get(
            **{search_field: object_id})
        return context


class MemberView(StatusFilterUnifiedView):
    template_name = "core/member.html"
    parent_model = MEMBER_MODEL

    def entry_index(request, template='myapp/entry_index.html'):
        context = {
            'entries': MemberView.objects.all(),
        }
        return render_to_response(
            template, context, context_instance=RequestContext(request))

    def get_queryset(self, **kwargs):
        self.persona = get_object_or_404(MEMBER_MODEL,
                                         id=self.kwargs['id']).facebook_persona
        if self.persona is None:
            return []
        return apply_request_params(
            self.persona.get_main_feed.facebook_status_set, self.request)

    def get_context_data(self, **kwargs):
        context = super(MemberView, self).get_context_data(**kwargs)
        if self.persona is None:
            return context
        feed = self.persona.get_main_feed

        dif_dict = feed.popularity_dif(params.POPULARITY_DIF_DAYS_BACK)
        context['change_in_popularity'] = dif_dict
        time_since_updated = timezone.now() - feed.locally_updated
        context['time_since_updated'] = time_since_updated.days

        return context


class PartyView(StatusFilterUnifiedView):
    template_name = "core/party.html"
    parent_model = PARTY_MODEL

    def get_queryset(self, **kwargs):
        search_string = self.kwargs['id']
        party = get_object_or_404(PARTY_MODEL, id=search_string)
        all_members_for_party = party.current_members()
        all_feeds_for_party = [
            member.facebook_persona.get_main_feed for member
            in all_members_for_party if member.facebook_persona]
        return apply_request_params(
            Facebook_Status.objects.filter(
                feed__id__in=[feed.id for feed in all_feeds_for_party]),
            self.request)


# TOFIx..
class PartyMembersView(StatusFilterUnifiedView):
    template_name = "core/party_members.html"
    parent_model = PARTY_MODEL

    def get_queryset(self, **kwargs):
        search_string = self.kwargs['id']
        party = get_object_or_404(PARTY_MODEL, id=search_string)
        all_members_for_party = party.current_members()
        all_feeds_for_party = [member.facebook_persona.get_main_feed for member
                               in
                               all_members_for_party if
                               member.facebook_persona]
        return apply_request_params(
            Facebook_Status.objects.filter(
                feed__id__in=[feed.id for feed in all_feeds_for_party]),
            self.request)


class TagView(StatusFilterUnifiedView):
    template_name = "core/tag.html"
    parent_model = Tag

    def dispatch(self, request, *args, **kwargs):
        if request.method.lower() in self.http_method_names:
            handler = getattr(self, request.method.lower(),
                              self.http_method_not_allowed)
        else:
            handler = self.http_method_not_allowed
        try:
            return handler(request, *args, **kwargs)
        except HasSynonymError as e:
            return HttpResponseRedirect(e.redirect_url)

    def get_queryset(self, **kwargs):
        variable_column = self.kwargs['variable_column']
        search_value = self.kwargs['id']
        search_field = self.kwargs['search_field']
        if search_field == 'id':
            search_field = 'id'
        else:
            search_field = 'name'
        selected_filter = variable_column + '__' + search_field

        selected_tag = get_object_or_404(Tag, **{search_field: search_value})
        if selected_tag.synonyms.exists():
            # if has synonyms, add to queryset
            selected_filter = 'tags__in'
            search_value = [synonym.tag for synonym in
                            selected_tag.synonyms.all()]
            # also add the original proper tag!
            search_value.append(selected_tag)
        if hasattr(selected_tag, 'proper_form_of_tag'):
            # if is a synonym of another tag, redirect
            proper_tag = selected_tag.proper_form_of_tag.proper_form_of_tag
            url = reverse('tag', kwargs={'variable_column': 'tags',
                                         # 'context_object': 'tag',
                                         'search_field': 'id',
                                         'id': proper_tag.id})
            # return HttpResponseRedirect(url)
            raise HasSynonymError('has synonym, redirect', redirect_url=url)

        return apply_request_params(
            Facebook_Status.objects.filter(**{selected_filter: search_value}),
            self.request)

    def get_context_data(self, **kwargs):
        context = super(TagView, self).get_context_data(**kwargs)
        all_feeds_for_tag = Facebook_Feed.objects.filter(
            facebook_status__id__in=[status.id for status in
                                     context['object_list']]).distinct()
        context['side_bar_list'] = MEMBER_MODEL.objects.filter(
            id__in=[feed.persona.owner_id for feed in
                    all_feeds_for_tag]).distinct().order_by('name')
        return context


class FacebookStatusDetailView(DetailView):
    template_name = 'core/facebook_status_detail.html'

    model = Facebook_Status
    slug_field = 'status_id'

    def get_object(self, queryset=None):
        return get_object_or_404(Facebook_Status,
                                 status_id=self.kwargs['slug'])

    def get_queryset(self, **kwargs):
        return Facebook_Status.objects_no_filters.all()

    def get_context_data(self, **kwargs):
        context = super(FacebookStatusDetailView, self).get_context_data(
            **kwargs)
        context['now'] = timezone.now()
        context['member'] = MEMBER_MODEL.objects.get(
            id=context['object'].feed.persona.owner_id)
        return context


class AllMembers(ListView):
    template_name = 'core/all_members.html'
    model = PARTY_MODEL


class AllParties(ListView):
    template_name = 'core/all_parties.html'
    model = PARTY_MODEL


class AllTags(ListView):
    template_name = 'core/all_tags.html'
    model = Tag


class ReviewTagsView(AjaxListView):
    template_name = "core/review_tags.html"
    page_template = "core/review_tags.html"
    model = TaggedItem

    def get_queryset(self):
        queryset = TaggedItem.objects.all().order_by('-date_of_tagging')
        return queryset


# Views for getting facebook data using a user Token
def login_page(request):
    return render(request, 'core/login_page.html')


def get_data_from_facebook(request):
    """
    This Function creates or updates within our db a facebook token recieved
    from a user. After receiving the token, it is first extended into  a
    long-term user token (see
    https://developers.facebook.com/docs/facebook-login/access-tokens#extending for mored details) # noqa
    Next the token is saved in our db. Afterwards, the token is tested on all
    of our user-profile feeds, for each feed that the token works for, their
    relation will be saved in our db, for future use. At the end, the function
    redirects backwards into referrer url.
    """
    user_access_token = request.POST['access_token']
    graph = facebook.GraphAPI(access_token=user_access_token)
    # Extension into long-term token
    extended_access_token = graph.extend_access_token(
        settings.FACEBOOK_APP_ID,
        settings.FACEBOOK_SECRET_KEY)
    graph.access_token = extended_access_token['access_token']
    # create or update token for user in db
    user = graph.get_object('me')
    token, created = User_Token.objects.get_or_create(user_id=user['id'])
    if created:
        token.token = extended_access_token['access_token']
        token.user_id = user['id']
    token.token = extended_access_token['access_token']
    token.date_of_creation = timezone.now()
    token.date_of_expiration = timezone.now() + timezone.timedelta(
        seconds=int(extended_access_token['expires_in']))
    token.save()

    # add or update relevant feeds for token
    user_profile_feeds = Facebook_Feed.objects.filter(feed_type='UP')
    relevant_feeds = []
    logger.debug('checking %d user_profile feeds.' % len(user_profile_feeds))
    for i, feed in enumerate(user_profile_feeds):
        logger.debug('working on %d of %d, vendor_id: %s.' % (
            i + 1, len(user_profile_feeds), feed.vendor_id))
        try:
            statuses = graph.get_connections(feed.vendor_id, 'statuses')
            if statuses['data']:
                logger.debug('feed %s returns at least one result.' % feed)
                relevant_feeds.append(feed)
        except GraphAPIError:
            logger.debug('token not working for feed %s' % feed.vendor_id)
            continue
    logger.debug('working on %d of %d user_profile feeds.' % (
        len(relevant_feeds), len(user_profile_feeds)))
    for feed in relevant_feeds:
        token.feeds.add(feed)
    logger.debug('adding %d feeds to token' % len(relevant_feeds))
    token.save()

    return HttpResponse(content_type='application/json', status=200,
                        content=json.dumps({'msg': 'great success!'}))


# A handler for status_update ajax call from client
def status_update(request, status_id):
    status = Facebook_Status.objects_no_filters.get(status_id=status_id)

    response = HttpResponse(content_type="application/json", status=200)
    response_data = dict()
    response_data['id'] = status.status_id

    try:
        if status.needs_refresh and waffle.flag_is_active(
                request, flag_name='status_update_request'):
            update_status_command = updatestatus.Command()
            update_status_command.graph.access_token = (
                update_status_command.graph.get_app_access_token(
                    settings.FACEBOOK_APP_ID,
                    settings.FACEBOOK_SECRET_KEY))
            status_response_dict = (
                update_status_command.fetch_status_object_data(status_id))
            status_response_dict = status_response_dict or {}

            response_data['likes'] = getattr(
                getattr(getattr(status_response_dict, 'likes', 0), 'summary',
                        0),
                'total_count', 0)
            response_data['comments'] = getattr(
                getattr(getattr(status_response_dict, 'comments', 0),
                        'summary', 0),
                'total_count', 0)
            response_data['shares'] = getattr(
                getattr(status_response_dict, 'shares', 0), 'count', 0)

            try:
                update_status_command.update_status_object_in_db(
                    retrieved_status_data=status_response_dict,
                    status_object=status,
                    options={'force-update': True,
                             'force-attachment-update': True})
            finally:
                response.status_code = 200

    except KeyError as e:
        response.status_code = 500

    except GraphAPIError as e:
        response.status_code = 504

    except ValueError as e:
        raise e

    except Exception as e:
        logger.exception('status_update error:', e)
        raise

    finally:
        response_data['likes'] = _format_int(status.like_count)
        response_data['comments'] = _format_int(status.comment_count)
        response_data['shares'] = _format_int(status.share_count)
        response_data['id'] = status.status_id

        response.content = json.dumps(response_data)
        return response


def _format_int(x):
    return 0 if not x else "{:,}".format(x)


# A handler for add_tag_to_status ajax call from client
@csrf_protect
def add_tag_to_status(request):
    # Todo:
    """
    1. actually restrict unregistered people from adding a tag
    2. using POST method instead of GET method
    3. using single transaction for the whole process
    """
    response_data = dict()
    response_data['success'] = False
    status_id = request.GET["id"]
    response_data['id'] = status_id
    tag_name = request.GET["tag_str"].strip()
    try:
        if tag_name:
            # Kikartags-based tagging
            if not re.match(TAG_NAME_REGEX, tag_name, re.UNICODE):
                response_data['error'] = 'invalid characters in tag name'
                raise Exception("Invalid characters in tag")
            taggit_tag, created = Tag.objects.get_or_create(name=tag_name)
            if created:
                taggit_tag.name = tag_name
                taggit_tag.save()
            status = Facebook_Status.objects_no_filters.get(id=status_id)
            status.tags.user_aware_add(request.user, taggit_tag)
            status.save()
            response_data['tag'] = {'id': taggit_tag.id,
                                    'name': taggit_tag.name}
            response_data['success'] = True

            # Old Deprecated Tagging
            tag, created = OldTag.objects.get_or_create(name=tag_name)
            if created:
                tag.name = tag_name
                tag.is_for_main_display = True
                tag.save()
                # add status to tag statuses
            tag.statuses.add(status_id)
            tag.save()
        else:
            response_data['success'] = True  # Nothing to do

    except Exception as e:
        logger.error("ERROR AT ADDING STATUS TO TAG:", e)
        logger.error(status_id)

    finally:
        return HttpResponse(json.dumps(response_data),
                            content_type="application/json")


# A handler for the search bar request from the client
def search_bar(request):
    search_text = request.GET['text']

    response_data = {
        'number_of_results': 0,
        'results': []
    }

    if search_text.strip():
        # factory method to create a dynamic search result

        def result_factory(object_id, name, object_type, **additional_info):
            result = {
                'id': object_id,
                'name': name,
                'type': object_type
            }
            result.update(additional_info)
            response_data['number_of_results'] += 1
            return result

        try:
            for party in search_bar_parties(search_text):
                response_data['results'].append(
                    result_factory(party.id, party.name, "party"))

            for member in search_bar_members(search_text):
                response_data['results'].append(
                    result_factory(member.id, member.name, "member",
                                   party=member.current_party.name))

            for tag in search_bar_tags(search_text):
                response_data['results'].append(
                    result_factory(tag.id, tag.name, "tag"))

        except Exception as e:
            logger.error("search bar exception:", e)
            raise e

    return HttpResponse(json.dumps(response_data),
                        content_type="application/json")


def search_bar_parties(search_text):
    query_direct_name = Q(name__icontains=search_text)

    if params.IS_ELECTIONS_MODE:
        query_alternative_names = Q(
            candidatelistaltname__name__icontains=search_text)
    else:
        query_alternative_names = Q(partyaltname__name__icontains=search_text)

    combined_party_name_query = query_direct_name | query_alternative_names

    if params.IS_ELECTIONS_MODE:
        party_query = combined_party_name_query
    else:
        party_query = combined_party_name_query & Q(
            knesset__number=params.CURRENT_KNESSET_NUMBER)

    return PARTY_MODEL.objects.filter(party_query).distinct().order_by(
        'name')[:params.NUMBER_OF_SUGGESTIONS_IN_SEARCH_BAR]


def search_bar_members(search_text):
    # Members
    query_exact_name = Q(name__icontains=search_text)

    if params.IS_ELECTIONS_MODE:
        query_alternative_names = Q(
            person__personaltname__name__icontains=search_text)
        combined_member_name_query = Q(
            person__name__icontains=search_text) | query_alternative_names
        member_query = combined_member_name_query
        member_order_by = 'person__name'
    else:
        query_alternative_names = Q(memberaltname__name__icontains=search_text)
        combined_member_name_query = query_exact_name | query_alternative_names
        member_query = combined_member_name_query & Q(is_current=True)
        member_order_by = 'name'

    members = MEMBER_MODEL.objects.filter(member_query).distinct()
    return members.select_related('current_party').order_by(member_order_by)[
           :params.NUMBER_OF_SUGGESTIONS_IN_SEARCH_BAR]


def search_bar_tags(search_text):
    query_direct_name = Q(name__icontains=search_text)
    query_tag_synonyms = Q(synonyms__tag__name=search_text)
    combined_tag_name_query = query_direct_name | query_tag_synonyms

    return Tag.objects.filter_proper(
        combined_tag_name_query).distinct().order_by('name')[
           :params.NUMBER_OF_SUGGESTIONS_IN_SEARCH_BAR]


def return_suggested_tags(request, status_id):
    response_data = {
        'number_of_results': 0,
        'results': []
    }

    def result_factory(object_id, name, object_type, percent,
                       **additional_info):
        result = {
            'id': object_id,
            'name': name,
            'type': object_type,
            'percent': percent
        }
        result.update(additional_info)
        response_data['number_of_results'] += 1
        return result

    for tag in Facebook_Status.objects.get(status_id=status_id).suggested_tags(
            n=3):
        response_data['results'].append(
            result_factory(tag.id, tag.name, "tag", tag.percent))

    return HttpResponse(json.dumps(response_data),
                        content_type="application/json")


class WidgetView(DetailView):
    template_name = 'core/rss_widget_page.html'
    model = UserSearch

    def get_object(self, queryset=None):
        return UserSearch.objects.first()

    def get_context_data(self, **kwargs):
        context = super(WidgetView, self).get_context_data(**kwargs)
        context['object'] = {'title': 'latest', 'path': '/latest/feed/',
                             'latest': 'true'}
        return context


class CustomWidgetView(DetailView):
    template_name = 'core/rss_widget_page.html'
    model = UserSearch

    def get_object(self, queryset=None):
        return get_object_or_404(UserSearch, title=self.kwargs['title'])


def title_exists(request):
    if not request.GET.get('title', None):
        res = {'approved': False, 'message': 'No title supplied!'}
        return HttpResponse(content=json.dumps(res),
                            content_type="application/json")
    title = request.GET.get('title', None)
    try:
        user_search = UserSearch.objects.get(title=title)
    except UserSearch.DoesNotExist:
        res = {'approved': True,
               'message': 'ok, no title saved with this name'}
        return HttpResponse(content=json.dumps(res),
                            content_type="application/json")
    if user_search.user.id == request.user.id:
        res = {'approved': True, 'message': 'ok, title belongs to user'}
    else:
        res = {'approved': False,
               'message': (
                   'This title belongs to another user, please select another '
                   'one.')}
    return HttpResponse(content=json.dumps(res),
                        content_type="application/json")


@user_passes_test(lambda u: u.is_superuser)
def delete_queryset(request):
    res = {}
    title = request.POST.get('query-title')
    try:
        us = UserSearch.objects.get(title=title)
        us.delete()
        res = {'message': 'custom query deleted successfully'}
    except UserSearch.DoesNotExist:
        res = {
            'message': (
                'custom query deletion failed - no query with supplied '
                'title: {}'.format(title))}
    finally:
        return HttpResponse(content=json.dumps(res),
                            content_type="application/json")


@user_passes_test(lambda u: u.is_superuser)
def save_queryset_for_user(request):
    user = request.user
    qserializer = QSerializer(base64=True)
    query_params = unicode(request.POST.get('query').split('?')[-1])
    query_dict = QueryDict(query_params.encode('utf8'), encoding='utf8')
    fake_request = HttpRequest()
    fake_request.GET = query_dict

    params_dict = get_parsed_request(query_dict)
    q_object = parse_to_q_object(query_dict, params_dict)
    dumped_queryset = qserializer.dumps(q_object)

    title = request.POST.get('title')
    description = request.POST.get('description')
    q_object_date = filter_by_date(fake_request)

    date_range = qserializer.dumps(q_object_date)
    order_by = json.dumps(get_order_by(fake_request))

    us, created = UserSearch.objects.get_or_create(user=user, title=title)
    if not created and us.user != request.user:
        return HttpResponse(content=json.dumps(
            {'message': 'failure: User is not allowed to edit this query!'}),
            content_type="application/json")

    us.queryset = dumped_queryset
    us.path = request.POST.get('query')
    us.order_by = order_by
    us.date_range = date_range
    us.description = description
    us.save()

    logger.debug(us.queryset_dict)

    return HttpResponse(content=json.dumps({'message': 'success'}),
                        content_type="application/json")


class CustomView(SearchView):
    model = Facebook_Status
    context_object_name = 'filtered_statuses'
    template_name = "core/custom.html"

    def get_queryset(self, **kwargs):
        sv = get_object_or_404(UserSearch, title=self.kwargs['title'])
        query_filter = sv.queryset_q
        date_range = self.request.GET.get('range')
        if date_range and date_range != 'default':
            date_range_q = filter_by_date(self.request)
        else:
            date_range_q = sv.date_range_q

        if self.request.GET.get('order_by'):
            order_by = get_order_by(self.request)
        else:
            order_by = json.loads(sv.order_by)
        return Facebook_Status.objects.filter(query_filter).filter(
            date_range_q).order_by(*order_by)

    def get_context_data(self, **kwargs):
        context = super(CustomView, self).get_context_data(**kwargs)
        sv = UserSearch.objects.get(title=self.kwargs['title'])
        qserialzer = QSerializer()
        query_filter = qserialzer.loads(sv.queryset)

        context['saved_query'] = sv
        return_queryset = apply_request_params(
            Facebook_Status.objects.filter(query_filter), self.request)
        context['number_of_results'] = return_queryset.count()
        context['side_bar_parameter'] = (
            params.HOURS_SINCE_PUBLICATION_FOR_SIDE_BAR)

        return context


class CustomViewByID(CustomView):
    def get_queryset(self, **kwargs):
        sv = get_object_or_404(UserSearch, id=self.kwargs['id'])
        qserialzer = QSerializer()
        query_filter = qserialzer.loads(sv.queryset)
        return apply_request_params(
            Facebook_Status.objects.filter(query_filter), self.request)

    def get_context_data(self, **kwargs):
        context = super(CustomView, self).get_context_data(**kwargs)
        sv = UserSearch.objects.get(id=self.kwargs['id'])
        qserialzer = QSerializer()
        query_filter = qserialzer.loads(sv.queryset)

        context['saved_query'] = sv
        return_queryset = apply_request_params(
            Facebook_Status.objects.filter(query_filter), self.request)
        context['number_of_results'] = return_queryset.count()
        context['side_bar_parameter'] = (
            params.HOURS_SINCE_PUBLICATION_FOR_SIDE_BAR)

        return context


class AllCustomsView(ListView):
    template_name = 'core/customs_list.html'
    model = UserSearch


class CustomsByUserView(ListView):
    template_name = 'core/customs_list.html'
    model = UserSearch

    def dispatch(self, request, *args, **kwargs):
        try:
            User.objects.get(username=self.kwargs['username'])
        except User.DoesNotExist:
            return redirect(reverse('all-customs'))
        return super(CustomsByUserView, self).dispatch(request, *args,
                                                       **kwargs)

    def get_queryset(self):
        try:
            user = User.objects.get(username=self.kwargs['username'])
            return UserSearch.objects.filter(user__username=user.username)
        except User.DoesNotExist:
            raise

    def get_context_data(self, **kwargs):
        try:
            context = super(CustomsByUserView, self).get_context_data(**kwargs)
            context['requested_user'] = User.objects.get(
                username=self.kwargs['username'])
            return context
        except User.DoesNotExist:
            raise
