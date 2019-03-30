import sys
from optparse import make_option

from tqdm import tqdm

import pandas as pd

from django.core.management.base import BaseCommand

from persons.models import Person

from facebook_feeds.models import (
    Facebook_Feed,
    Facebook_Persona,
)

from polyorg.models import (
    Candidate,
    CandidateList,
)


class Command(BaseCommand):

    help = 'create feed, candidate, person from excel. candidate list must exist.'
    args = '<excel_filename>'

    option_list = BaseCommand.option_list + (
        #make_option(
        #    '-x',
        #    '--excel',
        #    action='',
        #    dest='',
        #)
    )

    def add_row(self, facebook_name, facebook_id, rasham_name, rasham_party):
        # TODO - allow facebook_id to be missing, GET it from https://findmyfbid.in/

        feed_exists = Facebook_Feed.objects.filter(vendor_id=facebook_id).exists()
        if feed_exists:
            print('feed for {facebook_name} / {facebook_id} already exists, please delete it first'.format(
                facebook_name=facebook_name, facebook_id=facebook_id
            ))
            return

        # must have candidate list from name in excel
        cl = CandidateList.objects.get(name=rasham_party)

        # create persona
        persona = Facebook_Persona()
        persona.save() # now we have an id

        # create feed, update persona
        ff = Facebook_Feed(
            vendor_id=facebook_id,
            username=facebook_name,
            persona=persona,
        )
        ff.save()
        ff.persona.main_feed = ff.id
        ff.persona.save()

        # create Person
        person, created = Person.objects.get_or_create(
            name=rasham_name,
        )

        # create Candidate

        candidate = Candidate(
            person=person,
            ordinal=100, # TODO - get from excel
            candidates_list=cl,
        )
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
        expected_columns = {'facebook_name', 'facebook_id', 'rasham_name', 'rasham_party'}
        assert set(df.columns) == expected_columns , 'missing one of the expected columns: {expected_columns}'

        for i, row in tqdm(df.iterrows()):
            self.add_row(**{k: row[k] for k in expected_columns})

