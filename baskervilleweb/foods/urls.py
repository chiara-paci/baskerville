from django.conf.urls import include, url
from django.conf import settings

from . import models,views

app_name="foods"

urlpatterns = [
    url(r'^(?P<uid>[^/]*?)/?$',
        views.CalendarUserView.as_view(),
        name="calendar_user"),
    url(r'^(?P<uid>[^/]*?)/(?P<year>\d{4})/?$',
        views.CalendarUserView.as_view(),
        name="calendar_user_year"),
    url(r'^(?P<uid>[^/]*?)/archive/?$',
        views.DiaryUserArchiveView.as_view(),
        name="archive_user"),
    url(r'^(?P<uid>[^/]*?)/(?P<year>\d{4})/week/(?P<week>\d+)/?$',
        views.DiaryWeekArchiveView.as_view(),
        name="archive_week"),
    url(r'^(?P<uid>[^/]*?)/(?P<year>\d{4})/(?P<month>[-\w]+)/(?P<day>\d+)/?$',
        views.DiaryDayArchiveView.as_view(),
        name="archive_day"),
    url(r'^(?P<uid>[^/]*?)/today/?$',
        #login_required(DiaryTodayArchiveView.as_view(allow_future=True),login_url='/admin/login/'),
        views.DiaryTodayArchiveView.as_view(allow_future=True),
        name="archive_today"),
    url(r'^add_diaries/?$',
        views.AddDiariesView.as_view(),
        name="add_diaries"),
]
