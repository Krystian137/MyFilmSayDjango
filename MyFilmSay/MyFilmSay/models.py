from django.db import models
from django.utils import timezone


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


# === USER ===
class User(models.Model):
    email = models.EmailField(unique=True)
    password = models.CharField(max_length=128)
    name = models.CharField(max_length=255)
    role = models.CharField(
        max_length=20,
        choices=RoleEnum.choices,
        default=RoleEnum.USER,
    )

    def is_admin(self):
        return self.role == RoleEnum.ADMIN

    def is_moderator(self):
        return self.role == RoleEnum.MODERATOR

    def is_user(self):
        return self.role == RoleEnum.USER

    def __str__(self):
        return self.email


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
