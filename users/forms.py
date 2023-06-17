from crispy_forms.helper import FormHelper
from crispy_forms.layout import ButtonHolder, Field, Layout, Submit
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import Member, Profile


class UserRegisterForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email", "password1", "password2"]

    def __init__(self, *args, **kwargs):
        super(UserRegisterForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({"class": "form-control"})


class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ["username", "email"]

    def __init__(self, *args, **kwargs):
        super(UserUpdateForm, self).__init__(*args, **kwargs)
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update({"class": "form-control"})


class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = Profile
        fields = ["c2_api_key", "c2_logbook_id"]
        widgets = {"c2_api_key": forms.PasswordInput(render_value=True)}

    def __init__(self, *args, **kwargs):
        super(ProfileUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", "Update"))
        self.helper.layout = Layout(
            Field("c2_logbook_id"),
            Field("c2_api_key"),
            ButtonHolder(Submit("submit", "Update", css_class="btn btn-primary")),
        )
        for field in iter(self.fields):
            self.fields[field].widget.attrs.update(
                {
                    "class": "form-control",
                }
            )
            self.fields["c2_api_key"].widget.attrs.update(
                {
                    "title": "This is the API Key from log.concept2.com, "
                    "which is "
                    "used to synchronize your workouts from the concept2 "
                    "logbook with the Erganiser.",
                    "data-toggle": "tooltip",
                    "data-placement": "top",
                }
            )


class MemberUpdateForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ["squad", "sex"]

    def __init__(self, *args, **kwargs):
        super(MemberUpdateForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = "post"
        self.helper.add_input(Submit("submit", "Update"))
        self.helper.layout = Layout(
            Field("squad"),
            Field("sex"),
            ButtonHolder(Submit("submit", "Update", css_class="btn btn-primary")),
        )
