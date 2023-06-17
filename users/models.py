import uuid

from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _


# Create your models here.


class Squad(models.Model):
    """
    2nd stage: To address ergs and workouts for different squads
    """

    id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)
    squad_name = models.CharField(max_length=500)

    def __str__(self):
        return "%s squad" % self.squad_name


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    c2_api_key = models.CharField(max_length=250, blank=True, null=True)
    c2_refresh_key = models.CharField(max_length=250, blank=True, null=True)
    c2_logbook_id = models.CharField(max_length=250, blank=True, null=True)
    last_c2_sync = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Profile {self.user.username}"

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)

        # img = Image.open(self.image.path)
        # if img.height > 300 or img.width > 300:
        #     output_size = (300, 300)
        #     img.thumbnail(output_size)
        #     img.save(self.image.path)


class Role(models.Model):
    class Meta:
        verbose_name_plural = "Club Role"
        ordering = ["code"]

    """Role in the club this can be Coach, Member, Captain, ViceCaptain,
    SquadCaptain etc."""
    id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)
    code = models.CharField(max_length=2)
    description = models.CharField(max_length=255)

    def __str__(self):
        return "%s : %s" % (self.code, self.description)


class Member(models.Model):
    """This model handles all the club intern members"""

    squad = models.ForeignKey(Squad, on_delete=models.CASCADE, blank=True, null=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    role_code = models.ManyToManyField(Role, blank=True)
    coached_by = models.ManyToManyField("self", blank=True)
    is_coach = models.BooleanField(default=False)
    name = models.CharField(max_length=255, null=True, blank=True)
    sex = models.CharField(
        max_length=1,
        choices=[("f", _("female")), ("m", _("male")), ("o", _("other"))],
        blank=True,
        null=True,
    )

    def __str__(self):
        return self.user.username
