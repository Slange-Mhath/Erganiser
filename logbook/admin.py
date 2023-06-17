from django.contrib import admin

from .models import FinishedErg
from users.models import Squad

admin.site.register(FinishedErg)
admin.site.register(Squad)
