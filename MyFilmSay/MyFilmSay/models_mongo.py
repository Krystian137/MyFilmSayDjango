from mongoengine import (
    Document, EmbeddedDocument, fields
)
from datetime import datetime
import pytz
from enum import Enum
from mongoengine import CASCADE

class RoleEnum(str, Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"

def get_current_time():
    cet = pytz.timezone('Europe/Warsaw')
    now = datetime.now(cet)
    return now.replace(microsecond=0)

# === MOVIE ===
class Movie(Document):
    title = fields.StringField(required=True, unique=True, max_length=250)
    date = fields.StringField(required=True, max_length=250)
    body = fields.StringField(required=True)
    img_url = fields.StringField(max_length=250)
    rating = fields.FloatField()
    director = fields.StringField(max_length=250)
    writers = fields.StringField(max_length=250)
    genres = fields.StringField(max_length=250)

# === USER ===
class User(Document):
    email = fields.EmailField(required=True, unique=True)
    password = fields.StringField(required=True)
    name = fields.StringField(required=True)
    role = fields.StringField(default=RoleEnum.USER.value, choices=[e.value for e in RoleEnum])

    def is_admin(self):
        return self.role == RoleEnum.ADMIN.value

    def is_moderator(self):
        return self.role == RoleEnum.MODERATOR.value

    def is_user(self):
        return self.role == RoleEnum.USER.value

# === COMMENT ===
class Comment(Document):
    text = fields.StringField(required=True)
    author = fields.ReferenceField(User, reverse_delete_rule=CASCADE, required=True)
    timestamp = fields.DateTimeField(default=get_current_time)
    movie = fields.ReferenceField(Movie, reverse_delete_rule=CASCADE, required=True)
    user_rating = fields.FloatField()
    parent_id = fields.ReferenceField('self', null=True)  # dla wątku
    likes_count = fields.IntField(default=0)
    dislikes_count = fields.IntField(default=0)

# === COMMENT REPLY ===
class CommentReply(Document):
    comment = fields.ReferenceField(Comment, reverse_delete_rule=CASCADE)
    parent_id = fields.ReferenceField('self', null=True)
    reply_text = fields.StringField(required=True)
    author = fields.ReferenceField(User, reverse_delete_rule=CASCADE, required=True)
    timestamp = fields.DateTimeField(default=get_current_time)
    likes_count = fields.IntField(default=0)
    dislikes_count = fields.IntField(default=0)

# === VOTE ===
class Vote(Document):
    user = fields.ReferenceField(User, reverse_delete_rule=CASCADE, required=True)
    comment = fields.ReferenceField(Comment, reverse_delete_rule=CASCADE, required=True)
    vote_type = fields.StringField(required=True, choices=("like", "dislike"))
