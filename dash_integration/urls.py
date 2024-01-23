from django.urls import path
from . import views
from . import dash_chart

app_name = "dash_integration"

urlpatterns = [
    path('online/', views.Online.as_view(), name='online'),
    path('offline/', views.Offline.as_view(), name='offline'),
    path('dataplus/', views.DataPlus.as_view(), name='dataplus'),
    path('dataminus/', views.DataMinus.as_view(), name='dataminus'),
    path('datalook/<str:stock>/<int:page>', views.DataLook.as_view(), name='datalook'),
    path('usercheck/<str:page>', views.UserCheck.as_view(), name='usercheck'),
    # Other URL patterns
]