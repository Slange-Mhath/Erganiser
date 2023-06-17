import datetime

from django import forms
from django.core.validators import MaxValueValidator, MinValueValidator
from django.forms import ModelForm

from .models import FinishedErg


class DateInput(forms.DateInput):
    input_type = "date"


class BaseForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super(BaseForm, self).__init__(*args, **kwargs)
        for bound_field in self:
            if hasattr(bound_field, "field") and bound_field.field.required:
                bound_field.field.widget.attrs["required"] = "required"


class LogErgForm(BaseForm):
    avg_heartrate = forms.IntegerField(
        required=False,
        validators=[MaxValueValidator(300), MinValueValidator(0)],
        label="Avg HR",
    )
    avg_spm = forms.IntegerField(
        required=False,
        validators=[MaxValueValidator(100), MinValueValidator(0)],
        label="Avg SPM",
    )
    is_test = forms.BooleanField(
        required=False, initial=False, label="Enter time for your monthly " "Metrics"
    )

    class Meta:
        model = FinishedErg
        fields = [
            "name",
            "completed_at",
            "distance",
            "split_time",
            "result_time",
            "is_test",
            "avg_heartrate",
            "avg_spm",
        ]
        distance = forms.IntegerField(required=True)
        split_time = forms.DurationField(required=True)
        result_time = forms.DurationField(required=True)
        completed_at = forms.DateTimeField(required=True)
        avg_spm = (
            forms.IntegerField(
                required=False,
                validators=[MaxValueValidator(100), MinValueValidator(0)],
            ),
        )

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "value": f"Erg Workout from the: "
                    f"{datetime.date.today().strftime('%d/%m/%Y')}"
                }
            ),
            "completed_at": DateInput(attrs={"value": datetime.date.today()}),
            "result_time": forms.TextInput(attrs={"placeholder": "00:07:00"}),
            "distance": forms.TextInput(attrs={"placeholder": "2000"}),
            "split_time": forms.TextInput(attrs={"placeholder": "00:01:45"}),
            "effort": forms.Select(),
        }


class LogErgTestForm(BaseForm):
    class Meta:
        model = FinishedErg
        fields = [
            "name",
            "completed_at",
            "distance",
            "split_time",
            "avg_spm",
            "effort",
            "avg_heartrate",
            "result_time",
            "is_test",
        ]
        distance = forms.IntegerField(required=True)
        split_time = forms.DurationField(required=True)
        result_time = forms.DurationField(required=True)
        completed_at = forms.DateTimeField(required=True)
        avg_spm = (
            forms.IntegerField(
                required=False,
                validators=[MaxValueValidator(100), MinValueValidator(0)],
            ),
        )
        avg_heartrate = (
            forms.IntegerField(
                required=True, validators=[MaxValueValidator(300), MinValueValidator(0)]
            ),
        )
        widgets = {
            "name": forms.TextInput(
                attrs={
                    "value": f"Erg Workout from the: "
                    f"{datetime.date.today().strftime('%d/%m/%Y')}"
                }
            ),
            "completed_at": DateInput(attrs={"value": datetime.date.today()}),
            "result_time": forms.TextInput(attrs={"placeholder": "00:07:00"}),
            "distance": forms.TextInput(attrs={"placeholder": "2000"}),
            "split_time": forms.TextInput(attrs={"placeholder": "00:01:45"}),
        }


class UpdateErgForm(BaseForm):
    avg_heartrate = forms.IntegerField(
        required=False,
        validators=[MaxValueValidator(300), MinValueValidator(0)],
        label="Avg HR",
    )
    avg_spm = forms.IntegerField(
        required=False,
        validators=[MaxValueValidator(100), MinValueValidator(0)],
        label="Avg SPM",
    )
    is_test = forms.BooleanField(
        required=False, initial=False, label="Enter time for your monthly " "Metrics"
    )

    class Meta:
        model = FinishedErg
        fields = [
            "name",
            "completed_at",
            "distance",
            "split_time",
            "result_time",
            "is_test",
            "avg_heartrate",
            "avg_spm",
        ]
        distance = forms.IntegerField(required=True)
        split_time = forms.DurationField(required=True)
        result_time = forms.DurationField(required=True)
        completed_at = forms.DateTimeField(required=True)
        avg_spm = (
            forms.IntegerField(
                required=False,
                validators=[MaxValueValidator(100), MinValueValidator(0)],
            ),
        )

        widgets = {
            "name": forms.TextInput(
                attrs={
                    "value": f"Erg Workout from the: "
                    f"{datetime.date.today().strftime('%d/%m/%Y')}"
                }
            ),
            "completed_at": DateInput(),
            "result_time": forms.TextInput(attrs={"placeholder": "00:07:00"}),
            "distance": forms.TextInput(attrs={"placeholder": "2000"}),
            "split_time": forms.TextInput(attrs={"placeholder": "00:01:45"}),
            "effort": forms.Select(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["completed_at"].widget.attrs[
            "value"
        ] = self.instance.completed_at.strftime("%d/%m/%Y")
