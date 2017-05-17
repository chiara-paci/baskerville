from django.conf.urls import patterns, include, url
from django.contrib.staticfiles.urls import staticfiles_urlpatterns

from foods.views import DiaryDayArchiveView,DiaryTodayArchiveView,DiaryWeekArchiveView,AddDiariesView
from django.views.generic.dates import ArchiveIndexView
from foods.models import FoodDiaryEntry

from django.contrib.auth.decorators import login_required

urlpatterns = patterns('',
                       url(r'^(?P<uid>[^/]*?)/(?P<year>\d{4})/week/(?P<week>\d+)/?$',
                           DiaryWeekArchiveView.as_view(),
                           name="archive_week"),
                       url(r'^(?P<uid>[^/]*?)/(?P<year>\d{4})/(?P<month>[-\w]+)/(?P<day>\d+)/?$',
                           DiaryDayArchiveView.as_view(),
                           name="archive_day"),
                       url(r'^(?P<uid>[^/]*?)/today/?$',
                           #login_required(DiaryTodayArchiveView.as_view(allow_future=True),login_url='/admin/login/'),
                           DiaryTodayArchiveView.as_view(allow_future=True),
                           name="archive_today"),
                       url(r'^add_diaries/?$',
                           AddDiariesView.as_view(),
                           name="add_diaries"),
                       )