from django.urls import path
from .views import (
    SummaryView,
    CategorySummaryView,
    MonthlyTrendsView,
    RecentActivityView,
)

urlpatterns = [
    path('dashboard/summary/', SummaryView.as_view(), name='dashboard-summary'),
    path('dashboard/by-category/', CategorySummaryView.as_view(), name='dashboard-category'),
    path('dashboard/trends/', MonthlyTrendsView.as_view(), name='dashboard-trends'),
    path('dashboard/recent/', RecentActivityView.as_view(), name='dashboard-recent'),
]