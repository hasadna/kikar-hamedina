import factory
from mks import models
from knesset_factory import KnessetFactory


class PartyFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Party

    name = factory.sequence(lambda n: "Party {}".format(n))
    knesset = factory.SubFactory(KnessetFactory)
