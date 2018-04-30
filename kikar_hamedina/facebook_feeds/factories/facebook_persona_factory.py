from django.contrib.contenttypes.models import ContentType
import factory
from facebook_feeds import models


def member_content_type():
    return ContentType.objects.get(app_label="mks", model="member")


class FacebookPersonaFactory(factory.DjangoModelFactory):
    class Meta:
        model = models.Facebook_Persona

    content_type = member_content_type()
    object_id = None
    alt_content_type = None
    alt_object_id = None
    main_feed = None
