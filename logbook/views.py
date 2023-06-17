import calendar
import json
import random
from datetime import timedelta

import requests
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.exceptions import PermissionDenied
from django.db import IntegrityError
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils.datetime_safe import datetime
from django.utils.timezone import now
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    TemplateView,
    UpdateView,
)
from django.views.generic.dates import MonthArchiveView

from logbook.forms import LogErgForm, LogErgTestForm, UpdateErgForm
from users.models import Squad
from .models import FinishedErg


class Index(TemplateView):
    def get_template_names(self):
        if self.request.user.is_authenticated:
            template_name = "logbook/index.html"
        else:
            template_name = "logbook/login_required.html"
        return template_name

    def get_context_data(self, *, object_list=None, **kwargs):
        context = super().get_context_data(**kwargs)
        splits_to_display = []
        # squads_erg_tests = FinishedErg.objects.filter(is_test=True)
        if self.request.user.is_authenticated:
            # Get data for Recent Ergs
            my_last_ergs = FinishedErg.objects.filter(
                completed_by=self.request.user.member
            ).order_by("-completed_at")[:3]
            my_last_tests = FinishedErg.objects.filter(
                completed_by=self.request.user.member, is_test=True
            ).order_by("-completed_at")[:3]

            if self.request.user.member.is_coach:
                # Squad selection given from the template
                squad = self.request.GET.get("squad")
                if not squad:
                    # If no squad_id is selected just use s random one
                    squad_obj = random.choice(get_list_of_squads())
                    squad = squad_obj.id
                    context["current_squad"] = squad_obj
                else:
                    context["current_squad"] = Squad.objects.get(id=squad)
                erg_dist_of_month = get_erg_dist_of_month(squad)
                best_end_split_tests = get_best_erg_test_of_squad(
                    erg_dist_of_month, squad
                )
                top_three_splits = best_end_split_tests[:3]
                splits_to_display = top_three_splits

            else:
                # Identify which distance is given as test metrics for the
                # month
                if self.request.user.member.squad:
                    erg_dist_of_month = get_erg_dist_of_month(
                        self.request.user.member.squad.id
                    )
                    squad = self.request.user.member.squad.squad_name
                    # Get the three best erg scores for that distance in that
                    # month from the squad of the logged in user
                    best_end_split_tests = get_best_erg_test_of_squad(
                        erg_dist_of_month, self.request.user.member.squad.id
                    )
                    users_best_split = (
                        FinishedErg.objects.filter(
                            completed_by=self.request.user.member,
                            is_test=True,
                            completed_at__month=now().month,
                            distance=erg_dist_of_month,
                        )
                        .order_by("split_time")
                        .first()
                    )
                    top_three_splits = best_end_split_tests[:3]
                else:
                    users_best_split = None
                    erg_dist_of_month = None

                # Get the best split for that distance and month from the
                # currently logged in user to then see if he is in the top 3
                # Check if user is in top3, if so then just display the top3
                # and highlight him in it, if not display his position under
                # the top3 and highlight it in red

                if not users_best_split:
                    # USER has not entered an erg test
                    users_position = None

                elif users_best_split in top_three_splits:
                    # USERS test split is in the top 3 splits of the squad
                    splits_to_display = top_three_splits
                    users_position = list(splits_to_display).index(users_best_split) + 1

                else:
                    # USERS tests split is not in the top 3 splits of the squad
                    splits_to_display += top_three_splits
                    splits_to_display.append(users_best_split)
                    # Get position of users split in leaderboard
                    users_position = (
                        list(best_end_split_tests).index(users_best_split) + 1
                    )
                context["users_best_split"] = users_best_split
                context["users_position"] = users_position
                context["quote"] = get_rndm_motiv_quote(users_position)
                # context['current_squad'] = squad

            q = self.request.GET.get("isTest")
            if q == "True":
                my_last_ergs = my_last_tests

            context["my_last_ergs"] = my_last_ergs
            context["squads"] = get_list_of_squads()
            context["erg_dist_of_month"] = erg_dist_of_month
            context["current_month"] = now().month
            context["current_month_char"] = calendar.month_abbr[now().month]
            context["current_year"] = now().year
            context["splits_to_display"] = splits_to_display
            context["q"] = q
        return context


def get_rndm_motiv_quote(users_position):
    """
    This function returns a winning related quote, if the user is at the first
    place in his squad, otherwise it returns a random motivational quote.
    """
    with open("Erganiser/static/assets/data/quotes.json") as json_file:
        data = json.load(json_file)
        if users_position == "1":
            quotes = data["winner_quotes"]
        else:
            quotes = data["motivational_quotes"]
        quote = random.choice(quotes)
        return quote


def get_list_of_squads():
    squads = Squad.objects.all()
    return squads


def get_erg_dist_of_month(squad_id):
    """
    This function returns the distance of the erg test of the month for a given
    squad.
    """
    ergs_of_the_month = FinishedErg.objects.filter(
        completed_at__month=now().month, is_test=True, completed_by__squad__id=squad_id
    )
    if not ergs_of_the_month:
        return None
    this_month_dist = (
        ergs_of_the_month.values_list("distance", flat=True)
        .distinct()
        .order_by("-distance")
    )
    erg_endurance_dist = this_month_dist.first()
    return erg_endurance_dist


def get_best_erg_test_of_squad(dist_of_month, squad_id):
    """
    This orders the erg tests of the month by the split time to order the
    fastest erg tests first.
    """
    best_ergs = FinishedErg.objects.filter(
        completed_at__month=now().month,
        is_test=True,
        completed_by__squad__id=squad_id,
        distance=dist_of_month,
    ).order_by("split_time")
    return best_ergs


def convert_date_field(date):
    """
    This function converts a date string into a django datefield object.
    """
    date_object = datetime.strptime(date, "%Y-%m-%d %H:%M:%S")
    django_datefield = date_object.date()
    return django_datefield


def calculate_split_time(total_time, distance):
    """
    This function calculates the split time for a given distance and total time.
    """
    split_in_sec = 500 * ((total_time * 0.1) / distance)
    split = timedelta(seconds=round(split_in_sec))
    return split


def format_duration(time):
    """
    This function formats the duration of a workout into a timedelta object.
    """
    formatted_time = timedelta(seconds=round(time * 0.1))
    return formatted_time


def create_erg_object(workout, request):
    """
    This function creates an erg object in the database. It is used to store
    the results of an api call to get workouts done on a concept2 erg.
    https://log.concept2.com/developers/documentation/#logbook-users-results
    """
    try:
        erg = FinishedErg.objects.create(
            name="Concept2 {distance}m. Row".format(distance=workout["distance"]),
            c2_logbook_id=workout["id"],
            completed_by=request.user.member,
            distance=workout["distance"],
            avg_spm=workout["stroke_rate"] if "stroke_rate" in workout else None,
            completed_at=convert_date_field(workout["date"]),
            result_time=format_duration(workout["time"]),
            split_time=calculate_split_time(workout["time"], workout["distance"]),
            avg_heartrate=workout["heart_rate"]["average"]
            if "heart_rate" in workout and "average" in workout["heart_rate"]
            else None,
        )
        erg.save()
    except IntegrityError as e:
        if "logbook_finishederg_c2_logbook_id_key" in e.args[0]:
            messages.add_message(request, messages.INFO, "Already synced this Erg")
            return messages
    return erg


def get_results_api_call_url(user_profile, has_latest):
    """
    This function returns the url for the api call to get either all the
    workouts of a user or only the latest ones, which is determined by the
    has_latest parameter. The last_sync param in the user profile is used to
    determine the date from which the latest workouts should be synced.
    """
    url = (
        "https://log.concept2.com/api/users/{"
        "c2_logbook_id}/results?type=rower".format(
            c2_logbook_id=user_profile.c2_logbook_id
        )
    )
    if has_latest is not None:
        last_sync = user_profile.last_c2_sync.strftime("%Y-%m-%d %H:%M:%S")
        url += "&from={last_sync}".format(last_sync=last_sync)
    return url


def get_api_header(user_profile):
    headers = {"Authorization": "Bearer {token}".format(token=user_profile.c2_api_key)}
    return headers


@login_required
def sync_c2_erg_data(request, latest=None):
    """
    This function is used to sync the erg data from the concept2 logbook api.
    It calls the get_results_api_call url function first which returns the
    url according to the user decision to sync all or just the latest erg
    records from c2.
    It handles possible errors and displays an error message with the help
    of the django messages framework.
    If the api call is successful it calls a function to create and store the
    erg object in the db. It also adds the respective time of the syncing to the
    last synced parameter.
    """
    url = get_results_api_call_url(request.user.profile, latest)
    headers = get_api_header(request.user.profile)
    response = send_get_request_to_c2_api(url, headers)
    if response.status_code == 401:
        messages.add_message(
            request,
            messages.ERROR,
            "Connection Error: {error}: If this error persists try to delete "
            "the API Key in your profile and authorize yourself again."
            "".format(error=response.json()["message"]),
        )
        return HttpResponseRedirect(reverse("logbook:log-erg"))
    elif str(response.status_code).startswith("4") or str(
        response.status_code
    ).startswith("5"):
        messages.add_message(
            request,
            messages.ERROR,
            "Connection Error: {error}." "".format(error=response.json()["message"]),
        )
    data = response.json()
    if "data" not in data:
        messages.add_message(
            request, messages.ERROR, "C2 API Error: No data in response"
        )
        return HttpResponseRedirect(reverse("logbook:log-erg"))
    counter = 0
    for workout in data["data"]:
        erg = create_erg_object(workout, request)
        if erg is not None:
            request.user.profile.last_c2_sync = now()
            request.user.profile.save()
            counter += 1
    messages.add_message(
        request,
        messages.SUCCESS,
        "{} Erg Workouts "
        "from your "
        "Concept2 Logbook "
        "have been "
        "syncronised".format(counter),
    )
    return HttpResponseRedirect(reverse("logbook:erg-history"))


def send_get_request_to_c2_api(url, headers):
    response = requests.get(url, headers=headers, timeout=3)
    return response


class LogErg(LoginRequiredMixin, CreateView):
    """
    This class based view is used to enable the user to manually log an erg
    workout.
    """

    template_name = "logbook/log_erg.html"
    form_class = LogErgForm
    model = FinishedErg

    def form_valid(self, form):
        form.instance.completed_by = self.request.user.member
        form.save()
        return super().form_valid(form)


class LogErgTest(LoginRequiredMixin, CreateView):
    """
    This class based view is used to enable the user to manually log an erg
    workout. In hindisght this could have been done with the same view as the
    LogErg view, but I decided to keep it separate for now.
    """

    template_name = "logbook/log_erg.html"
    form_class = LogErgTestForm
    model = FinishedErg

    def form_valid(self, form):
        form.instance.completed_by = self.request.user.member
        form.save()
        return super().form_valid(form)


class ErgDetailView(LoginRequiredMixin, DetailView):
    """
    CBV to display the details of a finished erg workout.
    """

    template_name = "logbook/finished_erg_detail.html"
    model = FinishedErg

    def get_context_data(self, *args, **kwargs):
        context = super(ErgDetailView, self).get_context_data(**kwargs)
        return context


class MyErgHistory(LoginRequiredMixin, ListView):
    """
    CBV to display the erg history of the current user.
    """

    template_name = "logbook/erg_history.html"
    model = FinishedErg
    ordering = ["-completed_at"]
    paginate_by = 10

    def get_queryset(self):
        # Get the queryset for the ListView
        queryset = super().get_queryset()
        # Filter the queryset based on the current user
        queryset = queryset.filter(completed_by_id=self.request.user.member)
        # Return the filtered queryset
        return queryset


class ErgDeleteView(LoginRequiredMixin, DeleteView):
    """
    CBV to delete an erg workout.
    """

    model = FinishedErg
    template_name = "logbook/confirm_delete.html"

    def get_success_url(self):
        return reverse("logbook:erg-history")

    def dispatch(self, request, *args, **kwargs):
        erg = self.get_object()
        owner = erg.completed_by
        if owner != self.request.user.member:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class ErgUpdateView(LoginRequiredMixin, UpdateView):
    """
    CBV to update an erg workout.
    """

    model = FinishedErg
    form_class = UpdateErgForm

    template_name = "logbook/update_erg.html"

    def get_success_url(self):
        return reverse("logbook:erg-detail", kwargs={"pk": self.object.pk})

    def form_valid(self, form):
        form.instance.completed_by = self.request.user.member
        form.save()
        return super().form_valid(form)

    def dispatch(self, request, *args, **kwargs):
        erg = self.get_object()
        owner = erg.completed_by
        if owner != self.request.user.member:
            raise PermissionDenied
        return super().dispatch(request, *args, **kwargs)


class SquadScoreBoard(LoginRequiredMixin, MonthArchiveView):
    """
    This CBV is used to display the squad scoreboard. It is a subclass of the
    MonthArchiveView and uses the features to display the respective squads
    ergs for the current month in the current year, ordered by their split time.
    As we are almost always asked to provide 3 measurements for the scoreboard.
    (E.g. 100m, 500m, 2000m) I attempted a functionality to filter the
    displayed results for possible given distances. This is however yet still
    dependent on the correct input of the user.
    """

    model = FinishedErg
    date_field = "completed_at"
    allow_future = False
    allow_empty = True
    paginate_by = 10
    template_name = "logbook/squad-scoreboard.html"

    def get_context_data(self, *, object_list=None, **kwargs):
        current_month = self.get_month()
        current_year = self.get_year()
        distances = []
        context = super(SquadScoreBoard, self).get_context_data(**kwargs)
        if self.request.user.member.is_coach is False:
            erg_tests = FinishedErg.objects.filter(
                completed_at__year=current_year,
                completed_at__month=current_month,
                is_test=True,
                completed_by__squad=self.request.user.member.squad,
            ).order_by("result_time")
        else:
            # If user is coach get all erg tests
            # -------------------------------------
            erg_tests = FinishedErg.objects.filter(
                completed_at__year=current_year,
                completed_at__month=current_month,
                is_test=True,
            ).order_by("result_time")
            squads = Squad.objects.all()
            squads_erg_tests = {}
            q = self.request.GET.get("distance")
            for squad in squads:
                if q:
                    squads_erg_tests[squad.squad_name] = FinishedErg.objects.filter(
                        completed_at__year=current_year,
                        completed_at__month=current_month,
                        completed_by__squad=squad,
                        distance=q,
                        is_test=True,
                    ).order_by("result_time")
                else:
                    squads_erg_tests[squad.squad_name] = FinishedErg.objects.filter(
                        completed_at__year=current_year,
                        completed_at__month=current_month,
                        is_test=True,
                        completed_by__squad=squad,
                    ).order_by("result_time")
            context["squads_erg_tests"] = squads_erg_tests
        # ------------------------------------------------------------------------------------
        if not erg_tests:
            # If no erg tests are logged for the month, return empty context
            return context
        distances_of_erg_test = erg_tests.values_list("distance", flat=True).distinct()
        greatest_distance = max(distances_of_erg_test)
        if greatest_distance in distances_of_erg_test:
            distances.append(greatest_distance)
        half_distance = int(greatest_distance / 2)
        if half_distance in distances_of_erg_test:
            distances.append(half_distance)
        if 100 in distances_of_erg_test:
            distances.append(100)
        distances.sort()
        context["distances"] = distances
        context["erg_tests"] = erg_tests
        q = self.request.GET.get("distance")
        if q:
            queryset = FinishedErg.objects.filter(
                completed_at__year=current_year,
                completed_at__month=current_month,
                completed_by__squad=self.request.user.member.squad,
                distance=q,
                is_test=True,
            ).order_by("result_time")
            context["erg_tests"] = queryset
        return context
