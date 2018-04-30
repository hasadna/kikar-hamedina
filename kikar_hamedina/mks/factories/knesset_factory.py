import factory
from mks import models


class KnessetFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Knesset
        django_get_or_create = ('number',)

    number = factory.Sequence(lambda n: n)
