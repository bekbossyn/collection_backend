from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.conf import settings


# Create your models here.
class Collection(models.Model):
    collection = ArrayField(JSONField(default=dict, blank=True), default=list)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='collections', null=False, on_delete=models.CASCADE)

    def __str__(self):
        return u"Collection {0}".format(self.pk)

    def json(self, user=None):
        return {
            "user": self.user.json(short=False, user=self.user),
            "phone": self.hidden_phone(user),
            "name": self.name,
            "email": self.hidden_email(user),
            "avatar": get_url(self.avatar),
            "avatar_big": get_url(self.avatar_big) or get_url(self.avatar),
            # "languages": [l.name for l in self.languages.all()],
            "language_id": self.language,
            "language": self.get_language_display(),
            "review": self.review if self.review else None,
            # "reviews": [r.json(user) for r in self.reviews.all()],
            "verified": self.verified(),
            # 'game_setting': self.game_setting.json(user),
            "collections": self.collections.json(),
        }

    # class Meta:
    #     index_together = [
    #         ["token", "user"]
    #     ]


