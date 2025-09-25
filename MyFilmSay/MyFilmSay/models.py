from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager, PermissionsMixin


# === ROLE ENUM ===
class RoleEnum(models.TextChoices):
    USER = "user", "User"
    MODERATOR = "moderator", "Moderator"
    ADMIN = "admin", "Admin"


# === MOVIE ===
class Movie(models.Model):
    title = models.CharField(max_length=250, unique=True)
    date = models.CharField(max_length=250)
    body = models.TextField()
    img_url = models.CharField(max_length=250, blank=True, null=True)
    rating = models.FloatField(blank=True, null=True)
    director = models.CharField(max_length=250, blank=True, null=True)
    writers = models.CharField(max_length=250, blank=True, null=True)
    genres = models.CharField(max_length=250, blank=True, null=True)

    def __str__(self):
        return self.title


class MyUserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user

    def create_superuser(self, email, password, **extra_fields):
        extra_fields.setdefault('role', RoleEnum.ADMIN)
        user = self.create_user(email, password, **extra_fields)
        user.is_staff = True
        user.is_superuser = True
        user.save()
        return user

class User(AbstractBaseUser, PermissionsMixin):
    email = models.EmailField(unique=True)
    name = models.CharField(max_length=255)
    role = models.CharField(max_length=20, choices=RoleEnum.choices, default=RoleEnum.USER)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = MyUserManager()
    USERNAME_FIELD = 'email'

    @property
    def is_admin(self):
        return self.role == RoleEnum.ADMIN

    @property
    def is_moderator(self):
        return self.role == RoleEnum.MODERATOR

    @property
    def is_user(self):
        return self.role == RoleEnum.USER


# === COMMENT ===
class Comment(models.Model):
    text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    timestamp = models.DateTimeField(default=timezone.now)
    movie = models.ForeignKey(Movie, on_delete=models.CASCADE, related_name="comments")
    user_rating = models.FloatField(blank=True, null=True)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="replies")
    likes_count = models.IntegerField(default=0)
    dislikes_count = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.author.name}: {self.text[:30]}"


# === COMMENT REPLY ===
class CommentReply(models.Model):
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="replies_set")
    parent = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True, related_name="child_replies")
    reply_text = models.TextField()
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="replies")
    timestamp = models.DateTimeField(default=timezone.now)
    likes_count = models.IntegerField(default=0)
    dislikes_count = models.IntegerField(default=0)

    def __str__(self):
        return f"Reply by {self.author.name} to {self.comment.id}"


# === VOTE ===
class Vote(models.Model):
    VOTE_CHOICES = [
        ("like", "Like"),
        ("dislike", "Dislike"),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="votes")
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name="votes")
    vote_type = models.CharField(max_length=10, choices=VOTE_CHOICES)

    def __str__(self):
        return f"{self.user.email} voted {self.vote_type} on {self.comment.id}"
