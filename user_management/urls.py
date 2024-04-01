from django.urls import path
from .views import UserSignUpView, UserLoginView, ListUsersView, SearchUsers, \
SendFriendRequestView, RecievedPendingFriendRequests, AcceptRejectFriendRequest, ListFriends, \
SentPendingFriendRequests

urlpatterns = [
    path('sign-up/', UserSignUpView.as_view(), name='user_signup'),
    path('login/', UserLoginView.as_view(), name='user_login'),
    path('users-list/', ListUsersView.as_view(), name='users_list'),
    path('search-users/', SearchUsers.as_view(), name='search_users'),
    path('send-request/', SendFriendRequestView.as_view(), name='send_request'),
    path('pending-request/', RecievedPendingFriendRequests.as_view(), name='pending_request'),
    path('sent-pending-request/', SentPendingFriendRequests.as_view(), 
         name='sent_pending_request'),
    path('accept-reject_request/', AcceptRejectFriendRequest.as_view(), 
         name='accept_reject_request'),
    path('friends_list/', ListFriends.as_view(), name='friends_list'),
]