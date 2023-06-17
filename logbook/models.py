import uuid

from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from users.models import Member


class Erg(models.Model):
    c2_logbook_id = models.CharField(max_length=250, blank=True, null=True, unique=True)
    id = models.UUIDField("ID", primary_key=True, default=uuid.uuid4, editable=False)
    description = models.CharField(max_length=5000, blank=True, null=True)
    distance = models.PositiveIntegerField()
    name = models.CharField(max_length=200, blank=True, null=True)
    effort = models.CharField(
        max_length=8,
        choices=[
            ("low", _("low")),
            ("moderate", _("moderate")),
            ("intense", _("intense")),
        ],
        blank=True,
        null=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    split_time = models.DurationField()
    avg_spm = models.PositiveIntegerField(null=True, blank=True)
    avg_heartrate = models.PositiveIntegerField(null=True, blank=True)
    is_test = models.BooleanField(default=False)

    class Meta:
        abstract = True


# class PlannedErg(Erg):
#     """
#     2nd stage: Plan ergs, which needs to be done
#     """
#     est_time = models.DurationField(null=True, blank=True)
#     aimed_date = models.DateField(null=True, blank=True)
#     planned_for = models.ForeignKey(Squad, on_delete=models.CASCADE,
#     blank=True,
#                                     null=True)
#     created_by = models.ForeignKey(Member, related_name="creator",
#                                    on_delete=models.CASCADE, null=True)
#
#     def __str__(self):
#         return "Planned Erg %s" % self.name
#
#     # def get_absolute_url(self):
#     #     return reverse('logbook:planned_erg_detail',
#     #                    kwargs={'pk': self.pk})


class FinishedErg(Erg):
    """
    log your finished erg in here
    """

    completed_at = models.DateField()
    result_time = models.DurationField(null=True)
    completed_by = models.ForeignKey(
        Member, on_delete=models.CASCADE, null=True
    )  # This should never be null

    # planned_erg = models.ForeignKey(to=PlannedErg,
    #                                 on_delete=models.CASCADE, blank=True,
    #                                 null=True)

    def __str__(self):
        return "Completed Erg %s" % self.name

    def get_absolute_url(self):
        return reverse("logbook:erg-detail", kwargs={"pk": self.pk})

    def save(self, *args, **kwargs):
        if not self.name:
            self.name = f"{self.distance}m. Row"
        super().save(*args, **kwargs)


# class PlannedWorkout(models.Model):
#     """
#     2nd stage: You can plan multiple ergs for one workout
#     """
#     created_at = models.DateTimeField(auto_now_add=True)
#     id = models.UUIDField('ID', primary_key=True,
#                           default=uuid.uuid4, editable=False)
#     planned_erg = models.ForeignKey(PlannedErg, null=True, blank=True,
#                                     on_delete=models.CASCADE)
#
#
# class FinishedWorkout(models.Model):
#     """
#     Log multiple ergs in one workout
#     """
#     id = models.UUIDField('ID', primary_key=True,
#                           default=uuid.uuid4, editable=False)
#     finished_erg = models.ForeignKey(FinishedErg, null=True, blank=True,
#                                      on_delete=models.CASCADE)
#     planned_workout = models.ForeignKey(PlannedWorkout, null=True,
#                                         blank=True, on_delete=models.CASCADE)
#     completed_at = models.DateTimeField(null=True, blank=True)
#     completed_by = models.ForeignKey(Member, on_delete=models.CASCADE,
#                                      null=True)
