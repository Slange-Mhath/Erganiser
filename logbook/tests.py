# Create your tests here.
import datetime
import os
import random
from unittest.mock import Mock, patch

from django.contrib.auth.middleware import AuthenticationMiddleware
from django.contrib.auth.models import User
from django.contrib.messages import get_messages
from django.contrib.messages.middleware import MessageMiddleware
from django.contrib.sessions.middleware import SessionMiddleware
from django.http import HttpResponse
from django.test import Client, RequestFactory, TestCase
from django.urls import reverse
from django.utils import timezone

from logbook.models import FinishedErg
from logbook.views import (
    calculate_split_time,
    convert_date_field,
    create_erg_object,
    format_duration,
    get_api_header,
    get_results_api_call_url,
    sync_c2_erg_data,
)
from users.models import Profile, Squad


def get_random_date_of_current_month(self):
    now = datetime.datetime.now()
    year = now.year
    month = now.month
    num_days = (datetime.date(year, month + 1, 1) - datetime.date(year, month, 1)).days
    day = random.randint(1, num_days)
    random_date = datetime.datetime(year=year, month=month, day=day)
    return random_date


def get_response(request):
    return HttpResponse()


class CreateErgObjectDuplicateTest(TestCase):
    def setUp(self):
        self.request = RequestFactory().get("/")
        # Apply the middleware to the request
        middleware = SessionMiddleware(get_response(self.request))
        middleware.process_request(self.request)
        middleware = AuthenticationMiddleware(get_response(self.request))
        middleware.process_request(self.request)
        middleware = MessageMiddleware(get_response(self.request))
        middleware.process_request(self.request)
        self.workout = {
            "id": 1,
            "distance": 826,
            "date": "2019-11-18 09:45:32",
            "time_formatted": "3:32.4",
            "time": 2124,
            "heart_rate": {"average": 160},
            "stroke_rate": 24,
        }
        api_key = os.getenv("C2_API_KEY")
        refresh_api_key = os.getenv("C2_REFRESH_KEY")
        self.false_header = {
            "Authorization": "Bearer " "NrHM7099tGdq9STypWGNJqvSmmMqH26QDwexUKlaue"
        }
        self.get_results_url = (
            "https://log.concept2.com/api/users/1553112/results?type=rower"
        )
        self.get_wrong_results_url = (
            "https://log.concept3.com/api/users/1553112/results?type=rower"
        )
        self.get_latest_results_url = (
            "https://log.concept2.com/api/users/1553112/results?type=rower"
            "&from=2023-01-01"
        )
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpass"
        )
        self.profile, created = Profile.objects.get_or_create(user=self.user)
        self.request.user = self.user

        self.user.profile.c2_logbook_id = 1553112
        # This might need to be adjusted if the key expires.
        self.user.profile.c2_api_key = api_key
        self.user.profile.c2_refresh_key = refresh_api_key
        auth_header = f"Bearer {self.user.profile.c2_api_key}"
        self.header = {"Authorization": auth_header}
        self.user.profile.last_c2_sync = timezone.now()
        self.user.save()
        self.client.login(username="testuser", password="testpass")
        self.user2 = User.objects.create_user(
            username="testuser2", email="test2@test.com", password="testpass2"
        )
        self.profile2, created = Profile.objects.get_or_create(user=self.user2)
        self.user2.profile.c2_api_key = "sadsdwSdadsqsdqwdsdasdw"
        self.user2.profile.c2_logbook_id = 1553112
        self.user2.save()

    def test_create_erg_object(self):
        request = self.client.get("/get-erg-data/")
        http_request = request.wsgi_request
        http_request.user = self.user
        erg = create_erg_object(self.workout, http_request)
        self.assertEqual(erg.name, "Concept2 826m. Row")
        self.assertEqual(erg.c2_logbook_id, 1)
        self.assertEqual(erg.completed_by, self.user.member)
        self.assertEqual(erg.distance, 826)
        self.assertEqual(erg.avg_spm, 24)
        self.assertEqual(erg.completed_at.isoformat(), "2019-11-18")
        self.assertEqual(erg.result_time, datetime.timedelta(seconds=212))
        self.assertEqual(erg.split_time, datetime.timedelta(seconds=129))
        self.assertEqual(erg.avg_heartrate, 160)

    def test_format_duration(self):
        self.assertEqual(format_duration(10), datetime.timedelta(seconds=1))

    def test_calculate_split_time(self):
        # Checks that the time in tenth of seconds is calculating the right
        # split time in the right format.
        self.assertEqual(
            calculate_split_time(4200, 2000), datetime.timedelta(seconds=105)
        )

    def test_convert_date_field(self):
        date = "2020-02-14 09:30:15"
        self.assertEqual(convert_date_field(date), datetime.date(2020, 2, 14))

    def test_get_api_header(self):
        self.user.profile.c2_api_key = os.getenv("C2_API_KEY")
        self.user.save()
        api_header = get_api_header(self.user.profile)
        self.assertEqual(api_header, self.header)

    def test_get_results_api_call_url(self):
        url = get_results_api_call_url(self.user.profile, None)
        self.assertEqual(url, self.get_results_url)

    def test_get_latest_results_api_call_url(self):
        url = get_results_api_call_url(self.user.profile, "latest")
        date_now = timezone.now()
        self.assertIn(
            self.get_results_url + "&from=" + date_now.strftime("%Y-%m-%d"), url
        )


class IndexViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpass"
        )
        self.squad = Squad.objects.create(squad_name="Test Squad")
        self.user.member.squad = self.squad
        self.user.member.save()
        self.finished_erg1 = FinishedErg.objects.create(
            completed_by=self.user.member,
            completed_at=get_random_date_of_current_month(self),
            distance=2000,
            split_time=timezone.timedelta(seconds=180),
            is_test=True,
        )
        self.finished_erg2 = FinishedErg.objects.create(
            completed_by=self.user.member,
            distance=2000,
            completed_at=get_random_date_of_current_month(self),
            split_time=timezone.timedelta(seconds=360),
            is_test=True,
        )
        self.finished_erg3 = FinishedErg.objects.create(
            completed_by=self.user.member,
            completed_at=get_random_date_of_current_month(self),
            distance=500,
            split_time=timezone.timedelta(seconds=540),
            is_test=False,
        )

    def test_index_template_for_anonymous_user(self):
        response = self.client.get(reverse("logbook:index"))
        self.assertTemplateUsed(response, "logbook/login_required.html")

    def test_index_template_for_authenticated_user(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("logbook:index"))
        self.assertTemplateUsed(response, "logbook/index.html")

    def test_context_data_for_authenticated_user(self):
        self.client.login(username="testuser", password="testpass")
        response = self.client.get(reverse("logbook:index"))
        self.assertEqual(response.context["current_month"], timezone.now().month)
        self.assertEqual(response.context["current_year"], timezone.now().year)
        self.assertEqual(len(response.context["squads"]), 1)
        self.assertEqual(response.context["squads"][0], self.squad)

    def test_context_data_for_coach_user(self):
        self.client.login(username="testuser", password="testpass")
        self.user.member.is_coach = True
        self.user.member.save()
        self.finished_erg3.is_test = True
        self.finished_erg3.distance = 2000
        self.finished_erg3.save()
        response = self.client.get(reverse("logbook:index"))
        self.assertEqual(len(response.context["splits_to_display"]), 3)
        self.assertIsNotNone(response.context["current_squad"])

    def test_context_data_for_user_with_no_test(self):
        self.client.login(username="testuser", password="testpass")
        self.finished_erg1.delete()
        self.finished_erg2.delete()
        self.finished_erg3.delete()
        response = self.client.get(reverse("logbook:index"))
        self.assertIsNone(response.context["users_position"])
        self.assertIsNone(response.context["users_best_split"])

    def test_context_data_for_user_with_test_in_top_three(self):
        self.client.login(username="testuser", password="testpass")
        self.finished_erg1.is_test = True
        self.finished_erg2.is_test = True
        self.finished_erg3.distance = 2000
        self.finished_erg3.is_test = True
        self.finished_erg1.save()
        self.finished_erg2.save()
        self.finished_erg3.save()
        response = self.client.get(reverse("logbook:index"))
        self.assertEqual(len(response.context["splits_to_display"]), 3)
        self.assertEqual(response.context["users_best_split"].id, self.finished_erg1.id)
        self.assertEqual(response.context["users_position"], 1)


class SquadScoreBoardTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpass"
        )
        self.squad = Squad.objects.create(squad_name="Test Squad")
        self.user.member.squad = self.squad
        self.user.member.save()
        self.finished_erg1 = FinishedErg.objects.create(
            completed_by=self.user.member,
            completed_at="2023-04-01",
            distance=2000,
            split_time=timezone.timedelta(seconds=180),
            is_test=True,
        )
        self.finished_erg2 = FinishedErg.objects.create(
            completed_by=self.user.member,
            distance=2000,
            completed_at="2023-04-18",
            split_time=timezone.timedelta(seconds=360),
            is_test=True,
        )
        self.finished_erg3 = FinishedErg.objects.create(
            completed_by=self.user.member,
            completed_at="2023-04-10",
            distance=500,
            split_time=timezone.timedelta(seconds=540),
            is_test=False,
        )

    def test_login_required(self):
        year = 2023
        month = 4
        url = reverse("logbook:squad-scoreboard", args=[year, month])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, "/login/?next=/squad-scoreboard/2023%2F4")

    def test_view_url_exists_at_desired_location(self):
        self.client.login(username="testuser", password="testpass")
        year = 2023
        month = 4
        url = reverse("logbook:squad-scoreboard", args=[year, month])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        self.client.login(username="testuser", password="testpass")
        year = 2023
        month = 4
        url = reverse("logbook:squad-scoreboard", args=[year, month])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "logbook/squad-scoreboard.html")

    def test_erg_tests_filtered_by_month_and_squad(self):
        self.client.login(username="testuser", password="testpass")
        year = 2023
        month = 4
        url = reverse("logbook:squad-scoreboard", args=[year, month])
        response = self.client.get(url)
        erg_tests = response.context["erg_tests"]
        self.assertIn(self.finished_erg1, erg_tests)
        self.assertIn(self.finished_erg2, erg_tests)
        self.assertNotIn(self.finished_erg3, erg_tests)

    def test_erg_tests_filtered_by_month_and_coach(self):
        coach_user = User.objects.create_user(
            username="coach", email="coach@test.com", password="coachpass"
        )
        coach_user.member.is_coach = True
        coach_user.member.save()
        self.client.login(username="coach", password="coachpass")
        year = 2023
        month = 4
        url = reverse("logbook:squad-scoreboard", args=[year, month])
        response = self.client.get(url)
        erg_tests = response.context["erg_tests"]
        self.assertIn(self.finished_erg1, erg_tests)
        self.assertIn(self.finished_erg2, erg_tests)

    def test_erg_tests_sorted_by_result_time(self):
        self.client.login(username="testuser", password="testpass")
        year = 2023
        month = 4
        url = reverse("logbook:squad-scoreboard", args=[year, month])
        response = self.client.get(url)
        erg_tests = response.context["erg_tests"]
        self.assertEqual(list(erg_tests), [self.finished_erg1, self.finished_erg2])

        # Reverse the order of completed_at dates and assert that erg_tests
        # are sorted accordingly
        self.finished_erg1.completed_at = "2023-04-18"
        self.finished_erg1.save()
        self.finished_erg2.completed_at = "2023-04-01"
        self.finished_erg2.save()
        year = 2023
        month = 4
        url = reverse("logbook:squad-scoreboard", args=[year, month])
        response = self.client.get(url)
        erg_tests = response.context["erg_tests"]
        erg_ids = []
        for erg in erg_tests:
            erg_ids.append(erg.id)
        self.assertEqual(erg_ids, [self.finished_erg1.id, self.finished_erg2.id])

    def test_squad_scoreboard_view(self):
        self.client.login(username="testuser", password="testpass")

        # Test that the view returns a 200 response and uses the correct
        # template
        year = 2023
        month = 4
        url = reverse("logbook:squad-scoreboard", args=[year, month])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "logbook/squad-scoreboard.html")

        # Test that the context contains the correct data which should only
        # be the distance of the month which is 2000
        self.assertEqual(response.context["distances"], [2000])

        # Test that the context contains the correct data for a coach user
        coach_user = User.objects.create_user(
            username="coachuser", email="coach@test.com", password="coachpass"
        )
        coach_user.member.is_coach = True
        coach_user.member.save()
        self.client.login(username="coachuser", password="coachpass")
        year = 2023
        month = 4
        url = reverse("logbook:squad-scoreboard", args=[year, month])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["squads_erg_tests"]), 1)


class APICalls(TestCase):
    def setUp(self):
        self.request = RequestFactory().get("/")
        # Apply the middleware to the request
        middleware = SessionMiddleware(get_response(self.request))
        middleware.process_request(self.request)
        middleware = AuthenticationMiddleware(get_response(self.request))
        middleware.process_request(self.request)
        middleware = MessageMiddleware(get_response(self.request))
        middleware.process_request(self.request)
        self.get_results_url = (
            "https://log.concept2.com/api/users/1553112/results?type=rower"
        )
        self.get_wrong_results_url = (
            "https://log.concept3.com/api/users/1553112/results?type=rower"
        )
        self.get_latest_results_url = (
            "https://log.concept2.com/api/users/1553112/results?type=rower"
            "&from=2023-01-01"
        )
        self.user = User.objects.create_user(
            username="testuser", email="test@test.com", password="testpass"
        )
        self.profile, created = Profile.objects.get_or_create(user=self.user)
        self.request.user = self.user

        self.user.profile.c2_logbook_id = 1553112
        # This might need to be adjusted if the key expires.
        auth_header = f"Bearer {self.user.profile.c2_api_key}"
        self.header = {"Authorization": auth_header}
        self.user.profile.last_c2_sync = timezone.now()
        self.user.save()
        self.client.login(username="testuser", password="testpass")
        self.user2 = User.objects.create_user(
            username="testuser2", email="test2@test.com", password="testpass2"
        )
        self.profile2, created = Profile.objects.get_or_create(user=self.user2)
        self.user2.profile.c2_api_key = "sadsdwSdadsqsdqwdsdasdw"
        self.user2.profile.c2_logbook_id = 1553112
        self.user2.save()
        mock_c2_get_request = patch("logbook.views.send_get_request_to_c2_api")
        self.mock_c2_get_request = mock_c2_get_request.start()

        self.mock_ret_data = {
            "data": [
                {
                    "id": 60247291,
                    "user_id": 1553112,
                    "date": "2022-01-10 11:10:00",
                    "timezone": "Europe/London",
                    "date_utc": "2022-01-10 11:10:00",
                    "distance": 511,
                    "type": "rower",
                    "time": 1444,
                    "time_formatted": "2:24.4",
                    "workout_type": "JustRow",
                    "source": "ErgData iOS",
                    "weight_class": "H",
                    "verified": True,
                    "ranked": False,
                    "comments": None,
                    "stroke_data": True,
                    "calories_total": 29,
                    "drag_factor": 147,
                    "stroke_count": 20,
                    "stroke_rate": 30,
                    "workout": {
                        "splits": [
                            {
                                "type": "time",
                                "time": 1444,
                                "distance": 512,
                                "calories_total": 29,
                                "stroke_rate": 30,
                                "heart_rate": {"ending": 0},
                            }
                        ]
                    },
                    "real_time": None,
                },
                {
                    "id": 60087843,
                    "user_id": 1553112,
                    "date": "2022-01-06 13:19:00",
                    "timezone": "Europe/London",
                    "date_utc": "2022-01-06 13:19:00",
                    "distance": 3323,
                    "type": "rower",
                    "time": 8056,
                    "time_formatted": "13:25.6",
                    "workout_type": "JustRow",
                    "source": "ErgData iOS",
                    "weight_class": "H",
                    "verified": True,
                    "ranked": False,
                    "comments": None,
                    "stroke_data": True,
                    "calories_total": 218,
                    "drag_factor": 113,
                    "stroke_count": 311,
                    "stroke_rate": 24,
                    "workout": {
                        "splits": [
                            {
                                "type": "time",
                                "time": 3000,
                                "distance": 1245,
                                "calories_total": 82,
                                "stroke_rate": 24,
                                "heart_rate": {"ending": 0},
                            },
                            {
                                "type": "time",
                                "time": 3000,
                                "distance": 1254,
                                "calories_total": 83,
                                "stroke_rate": 24,
                                "heart_rate": {"ending": 0},
                            },
                            {
                                "type": "time",
                                "time": 2056,
                                "distance": 824,
                                "calories_total": 53,
                                "stroke_rate": 26,
                                "heart_rate": {"ending": 0},
                            },
                        ]
                    },
                    "real_time": None,
                },
                {
                    "id": 60006315,
                    "user_id": 1553112,
                    "date": "2022-01-04 12:47:00",
                    "timezone": "Europe/London",
                    "date_utc": "2022-01-04 12:47:00",
                    "distance": 3018,
                    "type": "rower",
                    "time": 7717,
                    "time_formatted": "12:51.7",
                    "workout_type": "JustRow",
                    "source": "ErgData iOS",
                    "weight_class": "H",
                    "verified": True,
                    "ranked": False,
                    "comments": None,
                    "stroke_data": True,
                    "calories_total": 188,
                    "drag_factor": 119,
                    "stroke_count": 253,
                    "stroke_rate": 19,
                    "workout": {
                        "splits": [
                            {
                                "type": "time",
                                "time": 3000,
                                "distance": 1190,
                                "calories_total": 75,
                                "stroke_rate": 20,
                                "heart_rate": {"ending": 0},
                            },
                            {
                                "type": "time",
                                "time": 3000,
                                "distance": 1205,
                                "calories_total": 77,
                                "stroke_rate": 20,
                                "heart_rate": {"ending": 0},
                            },
                            {
                                "type": "time",
                                "time": 1717,
                                "distance": 623,
                                "calories_total": 36,
                                "stroke_rate": 19,
                                "heart_rate": {"ending": 0},
                            },
                        ]
                    },
                    "real_time": None,
                },
                {
                    "id": 59370245,
                    "user_id": 1553112,
                    "date": "2021-12-14 15:51:00",
                    "timezone": "Europe/London",
                    "date_utc": "2021-12-14 15:51:00",
                    "distance": 2453,
                    "type": "rower",
                    "time": 6051,
                    "time_formatted": "10:05.1",
                    "workout_type": "JustRow",
                    "source": "ErgData iOS",
                    "weight_class": "H",
                    "verified": True,
                    "ranked": False,
                    "comments": None,
                    "stroke_data": True,
                    "calories_total": 157,
                    "drag_factor": 126,
                    "stroke_count": 243,
                    "stroke_rate": 23,
                    "workout": {
                        "splits": [
                            {
                                "type": "time",
                                "time": 3000,
                                "distance": 1209,
                                "calories_total": 77,
                                "stroke_rate": 24,
                                "heart_rate": {"ending": 0},
                            },
                            {
                                "type": "time",
                                "time": 3000,
                                "distance": 1228,
                                "calories_total": 80,
                                "stroke_rate": 24,
                                "heart_rate": {"ending": 0},
                            },
                            {
                                "type": "time",
                                "time": 51,
                                "distance": 16,
                                "calories_total": 0,
                                "heart_rate": {"ending": 0},
                            },
                        ]
                    },
                    "real_time": None,
                },
            ],
            "meta": {
                "pagination": {
                    "total": 59,
                    "count": 50,
                    "per_page": 50,
                    "current_page": 1,
                    "total_pages": 2,
                    "links": {
                        "next": "https://log.concept2.com/api/users/1553112"
                        "/results?type=rower&page=2"
                    },
                }
            },
        }

    def test_get_positive_c2_erg_data_response(self):
        mock_response = Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = self.mock_ret_data
        self.mock_c2_get_request.return_value = mock_response

        _ = sync_c2_erg_data(self.request, "None")
        messages = list(get_messages(self.request))
        self.assertEqual(
            str(messages[0]),
            f"{len(self.mock_ret_data['data'])} Erg Workouts "
            f"from your Concept2 Logbook have been syncronised",
        )
        user_ergs = FinishedErg.objects.filter(completed_by=self.request.user.member)
        self.assertEqual(len(user_ergs), len(self.mock_ret_data["data"]))

    def test_get_c2_erg_data_response_unauthorised_error(self):
        self.mock_c2_get_request.return_value.status_code = 401
        self.mock_c2_get_request.json.return_value = {"message": "Otto"}
        _ = sync_c2_erg_data(self.request, "None")
        messages = list(get_messages(self.request))
        error_message = (
            "If this error persists try to delete the API Key in "
            "your profile and authorize yourself again."
        )
        self.assertIn(error_message, str(messages[0]))

    def test_get_c2_erg_data_response_error(self):
        self.mock_c2_get_request.return_value.status_code = 404
        example_error = {"message": "This is an example error message"}
        self.mock_c2_get_request.return_value.json.return_value = example_error
        _ = sync_c2_erg_data(self.request, "None")
        messages = list(get_messages(self.request))
        self.assertEqual(
            str(messages[0]), f"Connection Error: " f"{example_error['message']}."
        )
