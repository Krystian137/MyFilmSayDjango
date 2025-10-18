from django.test import TestCase
from MyFilmSay.models import Movie, User, Comment, CommentReply, Vote, RoleEnum

class ModelTestCase(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(
            email="testuser@example.com",
            password="password",
            name="Test User"
        )
        self.movie = Movie.objects.create(
            title="Test Movie",
            date="2024-01-01",
            body="A test movie."
        )
        self.comment = Comment.objects.create(
            text="This is a test comment.",
            author=self.user,
            movie=self.movie
        )

    def test_movie_model(self):
        self.assertEqual(str(self.movie), "Test Movie")

    def test_user_model(self):
        self.assertEqual(self.user.email, "testuser@example.com")
        self.assertTrue(self.user.check_password("password"))
        self.assertEqual(self.user.name, "Test User")
        self.assertTrue(self.user.is_user)
        self.assertFalse(self.user.is_admin)
        self.assertFalse(self.user.is_moderator)

    def test_comment_model(self):
        self.assertEqual(str(self.comment), "Test User: This is a test comment.")
        self.assertEqual(self.comment.author, self.user)
        self.assertEqual(self.comment.movie, self.movie)

    def test_comment_reply_model(self):
        reply = CommentReply.objects.create(
            comment=self.comment,
            reply_text="This is a reply.",
            author=self.user
        )
        self.assertEqual(str(reply), f"Reply by Test User to {self.comment.id}")
        self.assertEqual(reply.comment, self.comment)
        self.assertEqual(reply.author, self.user)

    def test_vote_model(self):
        vote = Vote.objects.create(
            user=self.user,
            comment=self.comment,
            vote_type="like"
        )
        self.assertEqual(str(vote), f"testuser@example.com voted like on {self.comment}")
        self.assertEqual(vote.user, self.user)
        self.assertEqual(vote.comment, self.comment)
        self.assertEqual(vote.vote_type, "like")

    def test_user_roles(self):
        admin_user = User.objects.create_superuser(
            email="admin@example.com",
            password="adminpassword",
            name="Admin User"
        )
        self.assertTrue(admin_user.is_admin)
        self.assertFalse(admin_user.is_moderator)
        self.assertFalse(admin_user.is_user)

        moderator_user = User.objects.create_user(
            email="moderator@example.com",
            password="modpassword",
            name="Moderator User",
            role=RoleEnum.MODERATOR
        )
        self.assertFalse(moderator_user.is_admin)
        self.assertTrue(moderator_user.is_moderator)
        self.assertFalse(moderator_user.is_user)