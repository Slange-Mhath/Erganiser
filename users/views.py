import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth.models import User
from django.shortcuts import redirect, render
from verify_email.email_handler import send_verification_email

from Erganiser import settings
from .forms import MemberUpdateForm, ProfileUpdateForm, UserRegisterForm, UserUpdateForm


def register(request):
    """
    This view handles the registration of new users.
    """
    if request.method == "POST":
        u_form = UserRegisterForm(request.POST)
        if u_form.is_valid():
            email = u_form.cleaned_data.get("email")
            if User.objects.filter(email=email).exists():
                messages.error(
                    request,
                    "An account with that email address already exists. "
                    "Please use a different email address.",
                )
                return redirect("register")
            messages.success(
                request,
                "Your account has been created! Please check your email to "
                "verify your account before logging in.",
            )
            send_verification_email(request, u_form)
            return redirect("login")

    else:
        u_form = UserRegisterForm()

    context = {
        "u_form": u_form,
    }
    return render(request, "users/register.html", context)


@login_required
def profile(request):
    """
    This view handles the updating of user profiles. It combines the password
    reset form, the user form and the form to change profile information of
    the user.
    """
    if request.method == "POST":
        u_form = UserUpdateForm(request.POST, instance=request.user)
        m_form = MemberUpdateForm(request.POST, instance=request.user.member)
        p_form = ProfileUpdateForm(
            request.POST, request.FILES, instance=request.user.profile
        )
        pw_change_form = PasswordChangeForm(user=request.user, data=request.POST)
        if u_form.is_valid() and p_form.is_valid():
            u_form.save()
            m_form.save()
            p_form.save()
            messages.success(request, "Your account has been updated!")
            return redirect("profile")
        if pw_change_form.is_valid():
            pw_change_form.save()
            messages.success(request, "Your password has been updated!")
        else:
            messages.error(request, "Password not updated")
    else:
        u_form = UserUpdateForm(instance=request.user)
        m_form = MemberUpdateForm(instance=request.user.member)
        p_form = ProfileUpdateForm(instance=request.user.profile)
        pw_change_form = PasswordChangeForm(request.user.profile)

    context = {
        "u_form": u_form,
        "m_form": m_form,
        "p_form": p_form,
        "pw_change_form": pw_change_form,
    }

    return render(request, "users/profile.html", context)


def refresh_access_key(request):
    """
    This function refreshes the access key for the C2 API. It is called when
    the user already has an access key and wants to refresh it.
    https://log.concept2.com/developers/documentation/oauth
    """
    data = {
        "client_id": settings.C2_CLIENT_ID,
        "client_secret": settings.C2_CLIENT_SECRET,
        "grant_type": "refresh_token",
        "refresh_token": request.user.profile.c2_refresh_key,
        "redirect_uri": request.get_host() + "/oauth_with_c2",
        "scope": "user:read,results:read",
    }
    response = call_c2_oauth_api(data)
    return response


def get_access_key(request, auth_code):
    """
    This function gets the access key for the C2 API. It is called the first
    time the user authorises the app to access their C2 data.
    https://log.concept2.com/developers/documentation/oauth
    """
    base_url = request.build_absolute_uri("/")[:-1]
    data = {
        "client_id": settings.C2_CLIENT_ID,
        "client_secret": settings.C2_CLIENT_SECRET,
        "code": auth_code,
        "grant_type": "authorization_code",
        "redirect_uri": f"{base_url}/oauth_with_c2",
        "scope": "user:read,results:read",
    }
    response = call_c2_oauth_api(data)
    return response


def save_oauth_keys(response, request):
    """
    This function saves the access and refresh keys to the user's profile.
    """
    # Extract the access token from the response JSON
    access_token = response.json().get("access_token")
    refresh_token = response.json().get("refresh_token")
    user = request.user
    user.profile.c2_api_key = access_token
    user.profile.c2_refresh_key = refresh_token
    user.save()


def call_c2_oauth_api(data):
    """
    This function calls the C2 API to get the access key. It is called by both
    the get_access_key and refresh_access_key functions.
    https://log.concept2.com/developers/documentation/oauth
    """
    headers = {
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8",
        "Accept": "application/vnd.c2logbook.v1+json",
    }
    response = requests.post(
        "https://log.concept2.com/oauth/access_token", headers=headers, data=data
    )
    return response


def oauth_with_c2(request):
    """
    This view handles the different responses from the OAuth2 authorisation
    and renders the profile with an according message after.
    """
    auth_code = request.GET.get("code")
    if request.user.profile.c2_api_key:
        """
        This gets executed if the user already has a c2_api_key and thus
        already done the initial authorisation, so we just need to
        refresh.
        """
        response = refresh_access_key(request)
        if response.status_code == 200:
            save_oauth_keys(response, request)
            messages.success(request, "Your C2 API key has been refreshed")
            return render(request, "users/profile.html")
        elif str(response.status_code).startswith("4"):
            messages.error(request, response.content)
            return render(request, "users/profile.html")
    else:
        response = get_access_key(request, auth_code)
        if response.status_code == 200:
            save_oauth_keys(response, request)
            messages.success(request, "Your C2 API key has been saved")
            return render(request, "users/profile.html")
        elif str(response.status_code).startswith("4"):
            messages.error(request, response.content)
            return render(request, "users/profile.html")
