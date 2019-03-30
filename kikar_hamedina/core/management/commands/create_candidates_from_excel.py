import sys

import pandas as pd
from django.conf import settings
from django.core.management.base import BaseCommand
from tqdm import tqdm

from facebook_feeds.models import (
    Facebook_Feed,
    Facebook_Persona,
)
from persons.models import Person
from polyorg.models import (
    Candidate,
    CandidateList,
)


class Command(BaseCommand):
    help = 'create feed, candidate, person from excel. candidate list must exist.'
    args = '<excel_filename>'

    def add_row(self, facebook_name, facebook_id, rasham_name, rasham_party, candidate_list_position):
        # TODO - allow facebook_id to be missing, GET it from https://findmyfbid.in/

        # must have candidate list from name in excel
        cl = CandidateList.objects.get(name_he=rasham_party, knesset__number=settings.CURRENT_ELECTED_KNESSET_NUMBER)

        # create feed, update persona
        ff = Facebook_Feed.objects.filter(vendor_id=facebook_id).first()
        if ff is None:
            # create persona
            persona = Facebook_Persona()
            persona.save()  # now we have an id
            ff = Facebook_Feed(vendor_id=facebook_id, persona=persona)
        ff.username = facebook_name
        ff.save()
        ff.persona.main_feed = ff.id
        ff.persona.save()

        # create Person
        person, created = Person.objects.get_or_create(
            name_he=rasham_name,
        )

        # create Candidate

        candidate, created = Candidate.objects.get_or_create(
            person=person,
            candidates_list=cl,
            defaults={'ordinal': candidate_list_position}
        )
        candidate.ordinal = candidate_list_position
        candidate.save()

        # link candidate to persona
        ff.persona.alt_object_content = candidate
        ff.persona.save()

    def handle(self, *args, **options):

        if len(args) != 1:
            print('usage: {exe} <excel_filename>'.format(exe=sys.executable))
            raise SystemExit
        excel_filename = args[0]

        # take the first sheet - ignores the rest
        df = pd.read_excel(excel_filename)
        expected_columns = {'facebook_name', 'facebook_id', 'rasham_name', 'rasham_party', 'candidate_list_position'}
        assert set(df.columns) == expected_columns, 'missing one of the expected columns: {expected_columns}'

        for i, row in tqdm(df.iterrows()):
            self.add_row(**{k: row[k] for k in expected_columns})
