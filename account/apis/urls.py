from django.urls import path
from . import views


urlpatterns = [
    path("login/", views.Login.as_view(), name="login"),
    path("user/data/", views.UserListing.as_view(), name=" "),
    path("user/data/<int:user_id>/", views. UserDetail.as_view(), name="user-detail"),
    # path("user/<int:pk>/projects/", views. UserDetail.as_view(), name="user-detail"),
    # path("user/data/<int:emp_id>/", views. UserDetail.as_view(), name="user-detail"),
]