from django.test import TestCase
from MyFilmSay.forms import CreateMovieForm, RegisterForm, LoginForm, CommentForm, ReplyForm

class FormsTestCase(TestCase):
    def test_create_movie_form(self):
        form_data = {
            "title": "Test Movie",
            "date": "2024-01-01",
            "body": "A test movie."
        }
        form = CreateMovieForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_register_form(self):
        form_data = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "password123",
            "password_confirm": "password123"
        }
        form = RegisterForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_login_form(self):
        form_data = {
            "email": "test@example.com",
            "password": "password123"
        }
        form = LoginForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_comment_form(self):
        form_data = {
            "comment_text": "This is a test comment.",
            "user_rating": 8.0
        }
        form = CommentForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_reply_form(self):
        form_data = {
            "reply_text": "This is a test reply."
        }
        form = ReplyForm(data=form_data)
        self.assertTrue(form.is_valid())

    def test_create_movie_form_invalid(self):
        form_data = {
            "title": "",
            "date": "2024-01-01",
            "body": "A test movie."
        }
        form = CreateMovieForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_register_form_invalid(self):
        form_data = {
            "email": "test@example.com",
            "name": "Test User",
            "password": "password123",
            "password_confirm": "password456"
        }
        form = RegisterForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_login_form_invalid(self):
        form_data = {
            "email": "test@example.com",
            "password": ""
        }
        form = LoginForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_comment_form_invalid(self):
        form_data = {
            "comment_text": "",
            "user_rating": 8.0
        }
        form = CommentForm(data=form_data)
        self.assertFalse(form.is_valid())

    def test_reply_form_invalid(self):
        form_data = {
            "reply_text": ""
        }
        form = ReplyForm(data=form_data)
        self.assertFalse(form.is_valid())