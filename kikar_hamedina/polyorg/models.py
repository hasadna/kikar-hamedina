# encoding: utf-8
from django.db import models
from django.contrib.contenttypes import generic
from django.core.urlresolvers import reverse
from django.utils.translation import ugettext_lazy as _

from facebook_feeds.models import Facebook_Persona

from polyorg.managers import BetterManager, CurrentKnessetCandidateListManager, CurrentKnessetCandidatesManager, \
    KnessetManager


# Added by kikar

class CandidateListAltname(models.Model):
    member = models.ForeignKey('CandidateList')
    name = models.CharField(max_length=64)


class ElectedKnesset(models.Model):
    number = models.IntegerField(_('Elected Knesset number'), primary_key=True)
    start_date = models.DateField(_('Start date'), blank=True, null=True)
    end_date = models.DateField(_('End date'), blank=True, null=True)
    election_date = models.DateField(_('Election date'), blank=True, null=True)

    objects = KnessetManager()

    def __unicode__(self):
        return _(u'Knesset %(number)d') % {'number': self.number}

    def get_absolute_url(self):
        return reverse('parties-members-list', kwargs={'pk': self.number})


# end kikar


class CandidateList(models.Model):
    candidates = models.ManyToManyField('persons.Person', blank=True, through='Candidate')
    name = models.CharField(_('Name'), max_length=80)
    ballot = models.CharField(_('Ballot'), max_length=4)
    number_of_seats = models.IntegerField(blank=True, null=True)
    surplus_partner = models.ForeignKey('self', blank=True, null=True,
                                        help_text=_('The list with which is the surplus votes partner'))
    mpg_html_report = models.TextField(_('MPG report'), blank=True, null=True,
                                       help_text=_('The MPG report on the list, can use html'))
    img_url = models.URLField(blank=True)
    youtube_user = models.CharField(_('YouTube user'), max_length=80, null=True, blank=True)
    wikipedia_page = models.CharField(_('Wikipedia page'), max_length=512, null=True, blank=True)
    twitter_account = models.CharField(_('Twitter account'), max_length=80, null=True, blank=True)
    facebook_url = models.URLField(blank=True, null=True)
    platform = models.TextField(_('Platform'), blank=True, null=True)
    party = models.ForeignKey('Party', blank=True, null=True)

    # added by kikar-hamedina
    # party = models.ForeignKey('mks.Party', null=True, blank=True)  # Knesset party associated with list
    knesset = models.ForeignKey(ElectedKnesset, related_name='candidate_lists', db_index=True,
                                null=True, blank=True)

    objects = BetterManager()
    current_knesset = CurrentKnessetCandidateListManager()

    @property
    def ok_url(self):
        """Open Knesset URL (if exists)"""
        return None

    # end kikar hamedina

    def save(self, *args, **kwargs):
        super(CandidateList, self).save()
        if self.surplus_partner:
            self.surplus_partner.surplus_partner = self

    def getHeadName(self):
        return Candidate.objects.get(candidates_list=self, ordinal=1).person.name

    @property
    def member_ids(self):
        ''' return a list of all members id in the party '''
        mks = Candidate.objects.filter(candidates_list=self, person__mk__isnull=False)
        return mks.values_list('person__mk__id', flat=True)

    def current_members(self):
        ''' return a list of all candidates '''
        return Candidate.objects.filter(candidates_list=self)

    @property
    def current_members_with_active_public_facebook_persona(self):
        return self.current_members().filter(persona__isnull=False, persona__feeds__feed_type='PP')

    @property
    def number_of_members(self):
        return CandidateList.candidates.count()

    @models.permalink
    def get_absolute_url(self):
        return ('candidate-list-detail', [self.id])

    def __unicode__(self):
        return u'{} ({})'.format(self.name, self.knesset)


class Party(models.Model):
    name = models.CharField(max_length=64)
    accepts_memberships = models.BooleanField(default=True)

    def __unicode__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'parties'


class Candidate(models.Model):
    candidates_list = models.ForeignKey(CandidateList)
    person = models.ForeignKey('persons.Person')
    ordinal = models.IntegerField(_('Ordinal'))
    votes = models.IntegerField(_('Elected by #'), null=True, blank=True,
                                help_text=_('How many people voted for this person'))
    is_current = models.BooleanField(default=True, db_index=True)

    # added by kikar-hamedina
    persona = generic.GenericRelation(Facebook_Persona,
                                      content_type_field='alt_content_type', object_id_field='alt_object_id')

    objects = BetterManager()
    current_knesset = CurrentKnessetCandidatesManager()

    @property
    def name(self):
        return self.person.name

    @name.setter
    def name(self, value):
        self.person.name = value
        self.person.save()


    def get_mk(self):
        """Standard way to get mk. Currently this relies on Facebook_Persona,
        as the mapping, if exists, should be configured there. Another option
        is to return person.mk, but this might not be configured correctly.
        Note that in any case, this can be None for non-MK candidates"""
        return self.facebook_persona.content_object

    @property
    def facebook_persona(self):
        return self.persona.select_related().first()

    @property
    def has_facebook_persona(self):
        return self.persona.exists()

    @property
    def name(self):
        return self.person.name

    @property
    def current_party(self):
        return self.candidates_list

    @property
    def ok_url(self):
        mk = self.get_mk()
        return mk.ok_url if mk else None

    # end kikar hamedina


    class Meta:
        ordering = ('ordinal',)

    def __unicode__(self):
        return u"%s (%s)" % (self.person.name, self.id)
