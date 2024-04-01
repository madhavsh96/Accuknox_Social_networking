from .models import User, FriendRequestModel
from rest_framework import serializers
from django.contrib.auth import get_user_model


User = get_user_model()



class CreateUserSerializers(serializers.ModelSerializer):
    """
    serializer class for creating a new user
    """

    class Meta:
        model = User
        fields = ('id', 'email', 'password','first_name')

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user
    
    def to_representation(self, instance):
        response_data =  super().to_representation(instance)
        del response_data['password']
        return response_data
    
    
class SearchUsersSerializers(serializers.ModelSerializer):
    """
    serializer class to search users
    """

    class Meta:
        model = User
        fields = ['email','first_name']



class RecievedFriendRequestSerializers(serializers.Serializer):
    """
    serializer class for recieved friend requests
    """

    email = serializers.EmailField(source='request_sent_by.email')
    username = serializers.CharField(source='request_sent_by.first_name')
    class Meta:
        model = FriendRequestModel
        fields = ['email','username']


class SentFriendRequestSerializers(serializers.Serializer):
    """
    serializer class for sent friend requests
    """

    email = serializers.EmailField(source='request_sent_to.email')
    username = serializers.CharField(source='request_sent_to.first_name')
    class Meta:
        model = FriendRequestModel
        fields = ['email','username']


class ListFriendsSerializers(serializers.ModelSerializer):
    """
    serializer class for listing friends
    """
    
    class Meta:
        model = FriendRequestModel
        fields = []

    def to_representation(self, instance):

        response_data =  super().to_representation(instance)
        request = self.context.get('request')
        obj = instance.request_sent_to if instance.request_sent_by.email == request.user.email \
            else instance.request_sent_by
        response_data["email"] = obj.email
        response_data["username"] = obj.first_name
        return response_data

        