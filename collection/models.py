from django.contrib.postgres.fields import ArrayField, JSONField
from django.db import models
from django.conf import settings


# Create your models here.
class Collection(models.Model):
    # collection = ArrayField(JSONField(default=dict, blank=True), default=list)
    name = models.CharField(max_length=100, blank=True, null=True)
    # data = JSONField(default=dict, blank=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='collections', null=False, on_delete=models.CASCADE)

    def __str__(self):
        return u"Collection id {0} & name {1} of user {2}".format(self.pk, self.name, self.user.pk)

    def json(self, user=None):
        # collections = []
        # for index, item in enumerate(self.collection):
        #     collections.append(item)
        # return self.collection
        # return collections
        return {
            "collection_id": self.pk,
            "name": self.name,
            "words": [x.json(collection=self) for x in self.words.all()],
            "user_id": user.pk if user else None,
            # "collection": [x for x in self.collection],
            # "user": self.user.json(short=True),
            # "phone": self.hidden_phone(user),
            # "name": self.name,
            # "email": self.hidden_email(user),
            # "avatar": get_url(self.avatar),
            # "avatar_big": get_url(self.avatar_big) or get_url(self.avatar),
            # # "languages": [l.name for l in self.languages.all()],
            # "language_id": self.language,
            # "language": self.get_language_display(),
            # "review": self.review if self.review else None,
            # # "reviews": [r.json(user) for r in self.reviews.all()],
            # "verified": self.verified(),
            # # 'game_setting': self.game_setting.json(user),
            # "collections": self.collections.json(),
        }

    # class Meta:
    #     index_together = [
    #         ["token", "user"]
    #     ]


class Word(models.Model):
    # collection = ArrayField(JSONField(default=dict, blank=True), default=list)
    data = JSONField(default=dict, blank=True)
    collection = models.ForeignKey(Collection, related_name='words', blank=True, null=True, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='words', blank=True, null=True, on_delete=models.CASCADE)
    users = ArrayField(models.IntegerField(null=True, blank=True), default=list, blank=True, null=True)

    def __str__(self):
        return u"Word {0}".format(self.pk)

    def json(self, collection=None):
        return {
            "data": self.data,
            "collection": self.collection.name if collection else None,
            "user": self.user.pk if self.user else None,
            "users": [x for x in self.users],
        }
