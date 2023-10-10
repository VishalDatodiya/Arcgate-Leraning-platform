from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics

from account.apis.serializers import LoginSerializer, PermissionsSerializer
from drf_yasg.utils import swagger_auto_schema
from account.models import UserData, User
from account.apis import responses
from account.apis.pagination import PaginationHandlerMixin
from django.db import transaction


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "message": "Login Successfully!",
        "username": user.username,
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }


class Login(APIView):
    @swagger_auto_schema(request_body=LoginSerializer)
    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data["user"]
        token = get_tokens_for_user(user)
        return Response({"token": token}, status=status.HTTP_200_OK)


class BasicPagination(PageNumberPagination):
    page_size_query_param = "limit"


class UserListing(APIView, PaginationHandlerMixin):
    def get(self, request, *args, **kwargs):
        users_data = User.objects.get(pk=1)
        print(users_data.last_name)
        search_query = self.request.query_params.get("search")

        ordering = self.request.query_params.get("ordering", "id")

        project_filter = self.request.query_params.get("project")
        status_filter = self.request.query_params.get("status")
        empid_filter = self.request.query_params.get("permission")
        username_filter = self.request.query_params.get("username")
        fullName_filter = self.request.query_params.get("fullName")

        valid_ordering_fields = [
            "project__project_name",
            "permission__emp_id",
            "status",
            "users__username",
            "fullName",
            "id",
        ]
        if ordering.lstrip("-") not in valid_ordering_fields:
            ordering = "id"

        users_info = UserData.objects.all()

        users_info = users_info.order_by(ordering)

        if search_query:
            users_info = users_info.filter(
                project__project_name__icontains=search_query
            )

        if project_filter:
            users_info = users_info.filter(project__project_name=project_filter)

        if status_filter:
            users_info = users_info.filter(status=status_filter)

        if empid_filter:
            users_info = users_info.filter(permission__emp_id=empid_filter)

        if username_filter:
            users_info = users_info.filter(users__username=username_filter)

        if fullName_filter:
            users_info = users_info.filter(fullName__icontains=fullName_filter)

        if users_info.exists():
            page = self.paginate_queryset(users_info)

            if page is not None:
                serializer = PermissionsSerializer(page, many=True).data
                return self.get_paginated_response(serializer)
            try:
                serializer = PermissionsSerializer(users_info, many=True).data

                response_data = responses.success_response()
                return Response(response_data, status=status.HTTP_200_OK)
            
            except Exception as exe:
                error_message = f"Error: {str(exe)}"
                response_data = {'error': error_message}
                return Response(response_data, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        else:
            response_data = responses.error_response()
            return Response(response_data, status=status.HTTP_200_OK)


class BulkUpdateUserDataView(generics.UpdateAPIView):
    serializer_class = PermissionsSerializer

    @transaction.atomic
    def put(self, request, *args, **kwargs):
        updated_data = request.data

        if isinstance(updated_data, list):
            try:
                for item in updated_data:
                    user_id = item.get("user_id")
                    new_status = item.get("status")
                    new_permissions_data = item.get("permission")
                    project_name = item.get("project")
                    user_data_objects = UserData.objects.filter(
                        users__id=user_id, project__project_name=project_name
                    )

                    if user_data_objects.exists():
                        user_data = user_data_objects.first()

                        user_data.status = new_status
                        user_data.save()

                        permission = user_data.permission
                        permission.read = new_permissions_data.get(
                            "read", permission.read
                        )
                        permission.delete = new_permissions_data.get(
                            "delete", permission.delete
                        )
                        permission.update = new_permissions_data.get(
                            "update", permission.update
                        )
                        permission.save()

            except UserData.DoesNotExist:
                response_data = responses.user_data_not_found_response()
                return Response(response_data, status=status.HTTP_200_OK)

            return Response(
                {"message": f"Updated {len(updated_data)} user's data successfully"},
                status=status.HTTP_200_OK,
            )

        response_data = responses.invalid_data_formate_response()
        return Response(response_data, status=status.HTTP_200_OK)


class UserDetail(APIView):
    def get(self, request, user_id):
        try:
            user_data = UserData.objects.filter(users_id=user_id)

            if user_data.exists():
                serializer = PermissionsSerializer(user_data, many=True)

                response_data = responses.success_response(serializer.data)
                return Response(response_data, status=status.HTTP_200_OK)

            else:
                response_data = responses.failed_response()
                return Response(response_data, status=status.HTTP_200_OK)
        except:
            response_data = responses.error_response()
            return Response(response_data, status=status.HTTP_200_OK)