import django
import os
from mongoengine import connect
from werkzeug.security import generate_password_hash

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "demo.settings")
django.setup()

from MyFilmSay.models_mongo import User, RoleEnum

def create_admin():
    admin_email = "admin@admin.com"
    existing_admin = User.objects(email=admin_email).first()
    if existing_admin:
        print("Admin already exists!")
        return

    admin = User(
        email=admin_email,
        password=generate_password_hash("Admin", method="pbkdf2:sha256"),
        name="Admin",
        role=RoleEnum.ADMIN.value
    )
    admin.save()
    print("Admin added!")

if __name__ == "__main__":
    create_admin()
