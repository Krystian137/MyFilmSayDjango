from django.test import TestCase, Client
from django.urls import reverse
from MyFilmSay.models import User, Movie, Comment, RoleEnum
import json

class ViewsTestCase(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password",
            name="Test User"
        )
        self.admin_user = User.objects.create_superuser(
            email="admin@example.com",
            password="password",
            name="Admin User"
        )
        self.movie = Movie.objects.create(
            title="Test Movie",
            date="2024-01-01",
            body="A test movie."
        )

    def test_register_view(self):
        response = self.client.get(reverse("register"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "register.html")

        # Test successful registration
        response = self.client.post(reverse("register"), {
            "email": "newuser@example.com",
            "name": "New User",
            "password": "newpassword",
            "password_confirm": "newpassword"
        })
        self.assertEqual(response.status_code, 302)  # Redirects on success
        self.assertTrue(User.objects.filter(email="newuser@example.com").exists())

    def test_login_view(self):
        response = self.client.get(reverse("login"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "login.html")

        # Test successful login
        response = self.client.post(reverse("login"), {
            "email": "testuser@example.com",
            "password": "password"
        })
        self.assertEqual(response.status_code, 302)  # Redirects on success

    def test_logout_view(self):
        self.client.login(email="testuser@example.com", password="password")
        response = self.client.get(reverse("logout"))
        self.assertEqual(response.status_code, 302)  # Redirects on success

    def test_get_all_movies_view(self):
        response = self.client.get(reverse("get_all_movies"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "index.html")
        self.assertIn("all_movies", response.context)

    def test_show_movie_view(self):
        response = self.client.get(reverse("show_movie", args=[self.movie.id]))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "movie.html")
        self.assertEqual(response.context["movie"], self.movie)

    def test_add_movie_view_as_admin(self):
        self.client.login(email="admin@example.com", password="password")
        response = self.client.get(reverse("add_new_movie"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "make-movie.html")

    def test_add_movie_view_as_user(self):
        self.client.login(email="testuser@example.com", password="password")
        response = self.client.get(reverse("add_new_movie"))
        self.assertEqual(response.status_code, 302)  # Redirects if not admin

    def test_delete_movie_view(self):
        self.client.login(email="admin@example.com", password="password")
        response = self.client.post(reverse("delete_movie", args=[self.movie.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(Movie.objects.filter(id=self.movie.id).exists())

    def test_assign_role_view(self):
        self.client.login(email="admin@example.com", password="password")
        response = self.client.post(reverse("assign_role", args=[self.user.id, "moderator"]))
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.role, "moderator")

    def test_delete_user_view(self):
        self.client.login(email="admin@example.com", password="password")
        user_to_delete = User.objects.create_user(
            email="usertodelete@example.com",
            password="password",
            name="User to Delete"
        )
        response = self.client.post(reverse("delete_user", args=[user_to_delete.id]))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(User.objects.filter(id=user_to_delete.id).exists())

    def test_reply_comment_view(self):
        self.client.login(email="testuser@example.com", password="password")
        comment = Comment.objects.create(
            text="A comment to reply to.",
            author=self.user,
            movie=self.movie
        )
        response = self.client.post(reverse("reply_comment", args=[comment.id]), {
            "reply_text": "This is a reply."
        })
        self.assertEqual(response.status_code, 302)
        self.assertTrue(comment.replies_set.filter(reply_text="This is a reply.").exists())

    def test_vote_view(self):
        self.client.login(email="testuser@example.com", password="password")
        comment = Comment.objects.create(
            text="A comment to vote on.",
            author=self.user,
            movie=self.movie
        )
        response = self.client.post(
            reverse("vote"),
            json.dumps({"comment_id": f"comment-{comment.id}", "vote_type": "like"}),
            content_type="application/json"
        )
        self.assertEqual(response.status_code, 200)
        data = response.json()
        self.assertTrue(data["success"])
        self.assertEqual(data["likes"], 1)