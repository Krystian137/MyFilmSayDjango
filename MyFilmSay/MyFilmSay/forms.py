from django import forms
from django.core.validators import URLValidator, MinValueValidator, MaxValueValidator

class CreateMovieForm(forms.Form):
    title = forms.CharField(label="Title", max_length=250, required=True)
    img_url = forms.URLField(label="Movie Image URL", required=False, validators=[URLValidator()])
    body = forms.CharField(label="Movie Content", widget=forms.Textarea, required=True)
    date = forms.CharField(label="Date", max_length=250, required=True)
    rating = forms.FloatField(label="Rating", required=True)
    director = forms.CharField(label="Director", max_length=250, required=True)
    writers = forms.CharField(label="Writers", max_length=250, required=True)
    genres = forms.CharField(label="Genres", max_length=250, required=True)


class RegisterForm(forms.Form):
    name = forms.CharField(label="Name", max_length=100, required=True)
    email = forms.EmailField(label="Email", required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput, required=True)


class LoginForm(forms.Form):
    email = forms.EmailField(label="Email", required=True)
    password = forms.CharField(label="Password", widget=forms.PasswordInput, required=True)


class CommentForm(forms.Form):
    comment_text = forms.CharField(label="Comment", widget=forms.Textarea, required=True)
    user_rating = forms.FloatField(
        label="Your rating",
        required=False,
        validators=[MinValueValidator(1), MaxValueValidator(10)]
    )
    parent_id = forms.CharField(widget=forms.HiddenInput(), required=False)

    def clean(self):
        cleaned_data = super().clean()
        user_rating = cleaned_data.get("user_rating")
        parent_id = cleaned_data.get("parent_id")
        if not parent_id and user_rating is None:
            raise forms.ValidationError("Rating is required if this is not a reply.")


class ReplyForm(forms.Form):
    reply_text = forms.CharField(label="Reply", widget=forms.Textarea, required=True)


class FindMovieForm(forms.Form):
    title = forms.CharField(label="Movie Title", max_length=250, required=True)
