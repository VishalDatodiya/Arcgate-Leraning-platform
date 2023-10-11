from django.urls import path
from . import views


from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path("login/", views.Login.as_view(), name="login"),
    path('logout/', views.LogoutView.as_view(), name='auth_logout'),
    path("user/data/", views.UserListing.as_view(), name=" "),
    path("user/data/<int:user_id>/", views.UserDetail.as_view(), name="user-detail"),
    path(
        "user/update/",
        views.BulkUpdateUserDataView.as_view(),
        name="bulk-update-user-data",
    ),
    # path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/refresh/', views.TokenRefreshView.as_view(), name='token_refresh'),
    path('logout_all/', views.LogoutAllView.as_view(), name='auth_logout_all'),
]