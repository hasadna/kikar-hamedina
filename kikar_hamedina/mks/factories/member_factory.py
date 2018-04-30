import factory
from mks import models
from party_factory import PartyFactory


class MemberFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Member

    name = factory.sequence(lambda n: u"Name {}".format(n))
    name_en = factory.sequence(lambda n: u"Name {}".format(n))
    current_party = factory.SubFactory(PartyFactory)
    is_current = True
