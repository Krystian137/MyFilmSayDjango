from django import forms
from django.core.validators import URLValidator, MinValueValidator, MaxValueValidator
from .models import Movie


class CreateMovieForm(forms.ModelForm):
    class Meta:
        model = Movie
        fields = [
            "title", "img_url", "body", "date", "rating",
            "director", "writers", "genres"]


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
