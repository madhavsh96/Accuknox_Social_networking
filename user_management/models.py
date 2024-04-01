from django.db import models
from django.contrib.auth.models import BaseUserManager, AbstractBaseUser, PermissionsMixin

# Create your models here.

## friend request status
REQUEST_PENDING = 1
REQUEST_ACCEPTED = 2
REQUEST_REJECTED = 3

REQUEST_CHOICES = ((REQUEST_PENDING,"Pending"),(REQUEST_ACCEPTED,"Accepted"),
                   (REQUEST_REJECTED,"Rejected"))


class CustomUserManager(BaseUserManager):
    """
    class for customizing the user model manager class
    """

    def create_superuser(self, email, password, **other_fields):
        other_fields.setdefault('is_staff',True)
        other_fields.setdefault('is_superuser',True)
        other_fields.setdefault('is_active',True)

        return self.create_user(email, password, **other_fields)
    
    def create_user(self, email, password=None, **other_fields):
        if not email:
            raise ValueError('Email is required')
        email = self.normalize_email(email)
        user = self.model(email=email, **other_fields)
        if password:
            user.set_password(password)
        user.save()
        return user
    
class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True, blank=False)
    first_name = models.CharField(max_length=50, blank=True, null=True)
    is_staff = models.BooleanField(default=False)
    is_active = models.BooleanField(default=False)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.email
    

class FriendRequestModel(models.Model):
    """
    Model class to record the status of a friend request
    """

    request_sent_by = models.ForeignKey(User, null = True, on_delete=models.SET_NULL,
                                        related_name='user_sent_request')
    request_sent_to = models.ForeignKey(User, null = True, on_delete=models.SET_NULL,
                                        related_name='user_recieved_request')
    request_status = models.PositiveSmallIntegerField(choices=REQUEST_CHOICES, default=REQUEST_PENDING)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('request_sent_by', 'request_sent_to')
    
