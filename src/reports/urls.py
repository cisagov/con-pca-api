# Third-Party Libraries
from django.conf.urls import url
from django.urls import include, path
from reports.views import cycle_view, monthly_view, system_view, yearly_view

urlpatterns = [
    path(
        "<subscription_uuid>/monthly/<start_date>/",
        monthly_view.MonthlyReportsView.as_view(),
        name="monthly-reports-page",
    ),
    path(
        "<subscription_uuid>/cycle/<start_date>/",
        cycle_view.CycleReportsView.as_view(),
        name="cycle-reports-page",
    ),
    path(
        "<subscription_uuid>/yearly/<start_date>/",
        yearly_view.YearlyReportsView.as_view(),
        name="yearly-reports-page",
    ),
    path(
        "aggregate/",
        system_view.SystemReportsView.as_view(),
        name="system-reports-page",
    ),
    path(
        "<subscription_uuid>/subscription-stats-page/<start_date>/",
        cycle_view.CycleStatusView.as_view(),
        name="cycle-status",
    ),
]
