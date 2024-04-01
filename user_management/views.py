
from django.contrib.auth import authenticate, get_user_model
from django.contrib.auth.models import update_last_login
from django.db.models import Q
from django.core.cache import cache
from django.db import IntegrityError

from rest_framework.views import APIView
from rest_framework.generics import ListAPIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from rest_framework.authtoken.models import Token

import psycopg2

from .models import User, FriendRequestModel, REQUEST_PENDING, REQUEST_ACCEPTED, REQUEST_REJECTED
from .pagination import CustomPagination
from .serializers import CreateUserSerializers, SearchUsersSerializers, ListFriendsSerializers,\
RecievedFriendRequestSerializers, SentFriendRequestSerializers

User = get_user_model()

class UserSignUpView(APIView):
    """
    View class for handling user sign-up
    params: email, password and confirm_password
    """
    permission_classes = [AllowAny]
    serializer_class = CreateUserSerializers

    def post(self, request):

        request_data = request.POST.copy()

        ## if email or password or confirm_password are not present in request body return
        ## bad request status
        if not request_data.get('email') or not request_data.get('password') or not \
            request_data.get('confirm_password'):
            return Response({"error":"Email/Password is required"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        ## if password and confirm_password do not match, return bad request status
        if request_data.get('password') != request_data.get('confirm_password'):
            return Response({"error":"Passwords did not match"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        email = request_data.get('email')
        user = User.objects.filter(email=email)
        if user.exists():
            return Response({"error":"User already exists"}, 
            status=status.HTTP_400_BAD_REQUEST)
        else:
            request_data['password'] = request_data.get('password')
            request_data['email'] = email.lower()
            serializer_data = self.serializer_class(data=request_data)
            if serializer_data.is_valid():
                serializer_data.save()
                return Response(serializer_data.data,
                                status=status.HTTP_201_CREATED)
        
        return Response(serializer_data.errors, status=status.HTTP_400_BAD_REQUEST)
    

class UserLoginView(APIView):
    """
    View class for handling user login
    params: email and password
    """
    permission_classes = [AllowAny]

    def post(self, request):

        password = request.data.get('password')
        email = request.data.get('email')

        ## if email or password is none , return bad request status
        if not email or not password:
            return Response({"error":"Email/Password is required"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        ## convert email in lower case
        email = email.lower() 
        user = User.objects.filter(email=email)
        if user.exists():

            ## authenticating the user credentials
            user_obj = authenticate(request, username=email, password=password)
            if user_obj:

                ## if user is authenticated , generating a auth token
                token, created = Token.objects.get_or_create(user=user_obj)
                user_obj.is_active = True
                user_obj.save()

                # recording the login time
                update_last_login(None, user_obj)

                return Response({'message': 'User authentication completed', 'token': token.key}, 
                                 status=status.HTTP_200_OK)
            else:
                return Response({'detail': 'User credentials entered not correct'},
                                status=status.HTTP_401_UNAUTHORIZED)
        else:
            return Response({'detail': 'User is not registered'},
                            status=status.HTTP_401_UNAUTHORIZED)
        
class ListUsersView(ListAPIView):
    """
    View class to list all the existing users
    """
    permission_classes = [IsAdminUser]
    pagination_class = CustomPagination
    serializer_class = SearchUsersSerializers

    def get(self, request):

        all_users = User.objects.all()
        page = self.paginate_queryset(all_users)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            paginated_response = self.get_paginated_response(
                        serializer.data)
        return paginated_response

class SearchUsers(ListAPIView):
    """
    View class to search users based on a sub string
    param : keyword which will be used as a sub string
    """

    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    serializer_class = SearchUsersSerializers

    def post(self, request):

        keyword = request.data.get('keyword')
        if not keyword:
            return Response({"error":"search keyword is required"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        ## quering from db if the keyword is present in either email or first_name
        results = User.objects.filter(Q(email__contains=keyword)|Q(first_name__contains=keyword))
        page = self.paginate_queryset(results)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            paginated_response = self.get_paginated_response(
                        serializer.data)
        return paginated_response
    
class SendFriendRequestView(APIView):
    """
    View class to send a frined request
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):

        request_sent_to = request.data.get('request_sent_to').lower()
        if not request_sent_to:
            return Response({"error":"Email is required to send the friend request"}, 
                            status=status.HTTP_400_BAD_REQUEST)
        
        if request.user.email == request_sent_to:
            return Response({"error":"You can not send request to yourself"},
                            status=status.HTTP_403_FORBIDDEN)
        
        reciever_user = User.objects.filter(email=request_sent_to)
        if reciever_user.exists():
            try:
                ## setting a cache for storing the count of requests sent by a user
                key = f'friend_request_limit_{request.user.id}'
                count = cache.get(key, 0)
                count += 1

                ## set timeout for 60 seconds , cache will be deleted/reset  after 60 seconds
                cache.set(key, count, timeout=60)

                ## if count is greater than 3 , returning status too many requests with a message
                if count > 3:
                    return Response({"detail":"You have reached the friend request limit. Please try again later."},
                                    status=status.HTTP_429_TOO_MANY_REQUESTS)
                
                FriendRequestModel.objects.create(request_sent_by = request.user,
                                                request_sent_to = reciever_user.first())
                return Response({"detail":f"Friend request to {request_sent_to} has been sent successfully"},
                             status=status.HTTP_200_OK
                            )
            except IntegrityError as e:

                ## checking if the request sent by and request sent to already exists
                if isinstance(e.__cause__, psycopg2.errors.UniqueViolation):
                    return Response({"detail":"You are already friends"},
                                    status=status.HTTP_400_BAD_REQUEST)
                else:
                    return Response({"detail":e},
                                    status=status.HTTP_400_BAD_REQUEST)
            
        else:
            return Response({"detail":"This user is invalid"},status=status.HTTP_400_BAD_REQUEST)


class RecievedPendingFriendRequests(ListAPIView):
    """
    View class to see the list of recieved pending friend requests
    """

    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    serializer_class = RecievedFriendRequestSerializers

    def get(self, request):
        results = FriendRequestModel.objects.filter(request_sent_to = request.user,
                                                    request_status = REQUEST_PENDING)
        page = self.paginate_queryset(results)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            paginated_response = self.get_paginated_response(
                        serializer.data)
        return paginated_response

    
class SentPendingFriendRequests(ListAPIView):
    """
    View class to see the list of sent pending friend requests
    """

    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    serializer_class = SentFriendRequestSerializers

    def get(self, request):
        results = FriendRequestModel.objects.filter(request_sent_by = request.user,
                                                    request_status = REQUEST_PENDING)
        page = self.paginate_queryset(results)
        if page is not None:
            serializer = self.serializer_class(page, many=True)
            paginated_response = self.get_paginated_response(
                        serializer.data)
        return paginated_response

    

class AcceptRejectFriendRequest(APIView):
    """
    View class to accept/reject a friend request
    params: email of user and boolean value if request is accepted or not
    """

    permission_classes = [IsAuthenticated]

    def post(self, request):

        request_user_email = request.data.get('request_user_email')
        request_accepted = request.data.get('request_accepted')

        request_user_obj = User.objects.filter(email = request_user_email)
        if request_user_obj.exists():
            request_qs = FriendRequestModel.objects.filter(request_sent_to = request.user,
                                                       request_sent_by = request_user_obj.first(),
                                                       request_status = REQUEST_PENDING)
            if request_qs.exists():
                request_obj = request_qs.first()
                if request_accepted:
                    request_obj.request_status = REQUEST_ACCEPTED
                    request_obj.save()
                    return Response({"detail":f"You and {request_user_email} are now friends"},
                                status=status.HTTP_200_OK)
                else:
                    request_obj.request_status = REQUEST_REJECTED
                    request_obj.save()
                    return Response({"detail":"Friend request rejected"},
                                status=status.HTTP_200_OK)
            else:
                return Response({"error":"This friend request does not exists"},
                                status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({"detail":"The user who sent this request does not exists"},
                            status=status.HTTP_400_BAD_REQUEST)
        
class ListFriends(ListAPIView):
    """
    View class to see the list friends
    """

    permission_classes = [IsAuthenticated]
    pagination_class = CustomPagination
    serializer_class = ListFriendsSerializers

    def get(self, request):
        
        results = FriendRequestModel.objects.filter(Q(request_sent_by = request.user)|
                                                    Q(request_sent_to = request.user),
                                                    request_status = REQUEST_ACCEPTED)
        
        page = self.paginate_queryset(results)
        if page is not None:
            serializer = self.serializer_class(page, many=True,context={"request": request})
            paginated_response = self.get_paginated_response(
                        serializer.data)
        return paginated_response

        

