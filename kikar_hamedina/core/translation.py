from django.utils.translation import ugettext_lazy as _
from modeltranslation.translator import (
    TranslationOptions,
    register,
)

from core.models import PARTY_MODEL
from mks.models import Member
from persons.models import Person


@register(PARTY_MODEL)
class PartyModelTranslatorOptions(TranslationOptions):
    fields = ('name',)
    fallback_values = _('-- sorry, no translation provided --')


@register(Member)
class MemberModelTranslatorOptions(TranslationOptions):
    fields = ('name',)
    fallback_values = _('-- sorry, no translation provided --')


@register(Person)
class PersonModelTranslationOptions(TranslationOptions):
    fields = ('name',)
    fallback_values = _('-- sorry, no translation provided --')
