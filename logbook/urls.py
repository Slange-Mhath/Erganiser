from django.urls import path

from .views import (
    ErgDeleteView,
    ErgDetailView,
    ErgUpdateView,
    Index,
    LogErg,
    LogErgTest,
    MyErgHistory,
    SquadScoreBoard,
    sync_c2_erg_data,
)

app_name = "logbook"

urlpatterns = [
    path("", Index.as_view(), name="index"),
    path("log-erg", LogErg.as_view(), name="log-erg"),
    path("log-erg-test", LogErgTest.as_view(), name="log-erg-test"),
    path("erg-history", MyErgHistory.as_view(), name="erg-history"),
    path("erg-detail/<uuid:pk>", ErgDetailView.as_view(), name="erg-detail"),
    # path('erg-scores', SquadErgScores.as_view(), name='erg-scores'),
    path("update-erg/<uuid:pk>", ErgUpdateView.as_view(), name="update-erg"),
    path("delete-erg/<uuid:pk>", ErgDeleteView.as_view(), name="delete-erg"),
    path(
        "squad-scoreboard/<int:year>/<int:month>",
        SquadScoreBoard.as_view(month_format="%m"),
        name="squad-scoreboard",
    ),
    path("sync_c2_erg_data/", sync_c2_erg_data, name="sync_c2_erg_data"),
    path("sync_c2_erg_data/<str:latest>", sync_c2_erg_data, name="sync_c2_erg_data"),
]
