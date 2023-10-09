from rest_framework.response import Response
from rest_framework import status
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework.pagination import PageNumberPagination
from rest_framework import generics
from rest_framework.renderers import JSONRenderer

from account.apis.serializers import LoginSerializer, PermissionsSerializer
from drf_yasg.utils import swagger_auto_schema
from account.models import  UserData, User
from account.apis import messages, responses
from account.apis.pagination import PaginationHandlerMixin
# from account.apis.permissions import IsAdminOrReadOnly, IsAdminUser


def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        "message": "Login Successfully!",
        "email": user.email,
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
    # pagination_class = BasicPagination
    # renderer_classes = [JSONRenderer]


    # permission_classes = [IsAdminOrReadOnly]
    # permission_classes = [IsAdminUser]

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

        users_info =  UserData.objects.all()

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
                
                
                return Response(
                    {
                        "message": messages.get_success_message(),
                        "error": False,
                        "code": 200,
                        
                        "result": serializer,
                    },
                    status=status.HTTP_200_OK,
                )
            except Exception as e:
                return Response({"msg":"Invalid"})
        else:
            return Response(
                {
                    "message": messages.get_not_found_message(),
                    "error": True,
                    "code": 200,
                    "result": [],
                },
                status=status.HTTP_200_OK,
            )


class  UserDetail(APIView):
    def get(self, request, user_id):
        try:
            user_data =  UserData.objects.filter(users_id=user_id)
            # user_info = User.objects.get(id=user_id)

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

    # def put(self, request, user_id):
    #     user_data =  UserData.objects.filter(users_id=user_id)
    #     serializer = PermissionsSerializer(user_data, data=request.data)
    #     if serializer.is_valid():
    #         serializer.save()
    #         return Response(serializer.data, status=status.HTTP_200_OK)
    #     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    


# class  UserDetail(APIView):
#     def get(self, request, user_id):
#         user_data =  UserData.objects.filter(users_id=user_id)

#         if user_data.exists():
#             serializer = PermissionsSerializer(user_data, many=True)

#             # Create a custom dictionary with the desired fields
#             permission_data = [
#                 {
#                     "read": item["read"],
#                     "delete": item["delete"],
#                     "update": item["update"],
#                 }
#                 for item in serializer.data
#             ]

#             response = {"permissions": permission_data}
#             return Response(response)
#         else:
#             return Response({'detail': 'User not found.'}, status=status.HTTP_404_NOT_FOUND)



# class  UserDetail(APIView):
#     # permission_classes = [IsAdminOrReadOnly]
#     # permission_classes = [IsAdminUser]
#     renderer_classes = [JSONRenderer]

#     def get(self, request, pk):
#         user_detail =  User.objects.get(pk=pk)
#         user_name = user_detail.users.username
#         projects = Project.objects.all()
#         serializer = UserListingSerializer(user_detail)
#         response = {
#             "projects":projects,
#             "data": serializer.data,
#         }
#         return Response(response,  status=status.HTTP_200_OK)

#     def put(self, request, pk):
#         user_detail =  .objects.get(pk=pk)
#         serializer = UserListingSerializer(user_detail, data=request.data)
        
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data)
#         else:
#             return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)