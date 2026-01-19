from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib import messages
from django.contrib.auth.hashers import make_password
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods, require_POST
from .models import Movie, User, Comment, CommentReply, Vote, RoleEnum
from .forms import CreateMovieForm, RegisterForm, LoginForm, CommentForm, ReplyForm, FindMovieForm
from django.urls import reverse
import random
from .utils import admin_only, admin_or_moderator_only
import requests
import json
from django.utils.http import urlencode
import os
from dotenv import load_dotenv
from django.db import transaction
import logging

logger = logging.getLogger(__name__)

load_dotenv()

API_KEY = os.getenv("API_KEY_TMDb")
API_URL = "https://api.themoviedb.org/3/search/movie"
API_IMG_URL = "https://image.tmdb.org/t/p/w500"
MOVIE_DB_INFO_URL = "https://api.themoviedb.org/3/movie"
COMMENTS_PER_PAGE = 5


def is_admin(user):
    return user.is_authenticated and user.role == 'admin'


@login_required
@admin_only
def add_movie(request):
    if request.method == "POST":
        form = CreateMovieForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Movie added successfully!")
            return redirect("movies_list")
    else:
        form = CreateMovieForm()
    return render(request, "add_movie.html", {"form": form})


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            if User.objects.filter(email=email).exists():
                messages.warning(request, "You've already signed up with that email, log in instead!")
                return redirect('login')

            password = form.cleaned_data['password']
            hashed_password = make_password(password)

            with transaction.atomic():
                new_user = User(
                    email=email,
                    name=form.cleaned_data['name'],
                    password=hashed_password,
                )
                new_user.save()
                login(request, new_user)

            messages.success(request, f"Welcome, {new_user.name}!")
            return redirect('get_all_movies')
    else:
        form = RegisterForm()
    return render(request, 'register.html', {'form': form, 'current_user': None})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']

            user = authenticate(request, username=email, password=password)
            if user is not None:
                login(request, user)
                messages.success(request, f"Welcome, {user.name}!")
                return redirect('get_all_movies')
            else:
                messages.error(request, "Invalid email or password.")
                return redirect('login')
    else:
        form = LoginForm()
    return render(request, 'login.html', {'form': form})


@login_required  # POPRAWKA: Dodano dekorator
def assign_role(request, user_id, role):
    if not (request.user.is_admin or request.user.is_moderator):
        messages.error(request, "You do not have permission to assign role.")
        return redirect(reverse('index'))

    user = get_object_or_404(User, pk=user_id)

    valid_roles = [RoleEnum.USER.value, RoleEnum.MODERATOR.value, RoleEnum.ADMIN.value]
    if role not in valid_roles:
        messages.error(request, "Invalid role.")
        return redirect(reverse('index'))

    if role == RoleEnum.ADMIN.value and request.user.id == user.id:
        messages.error(request, "You cannot assign the admin role to yourself.")
        return redirect(reverse('index'))

    with transaction.atomic():
        user.role = role
        user.save()

    messages.success(request, f"Role {role} assigned to {user.name}.")
    return redirect(reverse('users'))


@login_required
@user_passes_test(is_admin, login_url='index')
def delete_user(request, user_id):
    user = get_object_or_404(User, id=user_id)

    if request.user.id == user.id:
        messages.error(request, "You cannot delete your own account.")
        return redirect('users')

    with transaction.atomic():
        user.delete()

    messages.success(request, f"User {user.name} has been deleted.")
    return redirect('users')


def logout_view(request):
    logout(request)
    return redirect('get_all_movies')


def get_all_movies(request):
    sort_by = request.GET.get('sort_by', 'title')
    if sort_by == 'rating':
        all_movies = Movie.objects.order_by('-rating')
    elif sort_by == 'date':
        all_movies = Movie.objects.order_by('-date')
    else:
        all_movies = Movie.objects.order_by('title')

    all_movies = list(all_movies)
    random_movies = random.sample(all_movies, 3) if len(all_movies) >= 3 else all_movies
    return render(request, 'index.html', {
        'all_movies': all_movies,
        'random_movies': random_movies,
        'current_sort': sort_by
    })


def search(request):
    if request.method == 'POST':
        query = request.POST.get('query')
        if query:
            results = Movie.objects.filter(title__icontains=query)
            return render(request, 'search_results.html', {'search_results': results, 'query': query})
    return render(request, 'search_results.html', {'search_results': [], 'query': ''})


def show_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    offset = int(request.GET.get("offset", 0))

    comment_form = CommentForm(request.POST or None)
    reply_form = ReplyForm()

    comments = Comment.objects.filter(movie_id=movie.id) \
                   .select_related('author') \
                   .prefetch_related('replies_set__author') \
                   .order_by('-id')[offset:offset + COMMENTS_PER_PAGE]

    total_comments = Comment.objects.filter(movie_id=movie.id).count()
    current_user_id = request.user.id if request.user.is_authenticated else None

    rating_percentage = movie.rating * 10 if movie.rating else 0
    star_range = range(1, 11)

    if request.method == "POST" and 'submit' in request.POST:
        if not request.user.is_authenticated:
            messages.warning(request, "You need to login or register to comment.")
            return redirect("login")

        if comment_form.is_valid():
            parent_id = comment_form.cleaned_data.get('parent_id')
            parent = Comment.objects.get(id=parent_id) if parent_id else None

            with transaction.atomic():
                Comment.objects.create(
                    text=comment_form.cleaned_data['comment_text'],
                    author=request.user,
                    movie=movie,
                    user_rating=comment_form.cleaned_data['user_rating'],
                    parent=parent
                )

            messages.success(request, "Comment added successfully!")
            return redirect('show_movie', movie_id=movie_id)
        else:
            messages.error(request, "Please correct the errors in the comment form.")

    return render(request, "movie.html", {
        "movie": movie,
        "form": comment_form,
        "reply_form": reply_form,
        "comments": comments,
        "total_comments": total_comments,
        "current_user": request.user,
        "current_user_id": current_user_id,
        "rating_percentage": rating_percentage,
        "offset": offset,
        "star_range": star_range,
    })


@login_required
def reply_comment(request, comment_id):
    reply_form = ReplyForm(request.POST)
    if reply_form.is_valid():
        reply_text = reply_form.cleaned_data['reply_text']
        parent_reply_id = request.POST.get("parent_reply_id")

        with transaction.atomic():
            if parent_reply_id:
                parent_reply = get_object_or_404(CommentReply, id=parent_reply_id)
                new_reply = CommentReply(
                    parent_id=parent_reply.id,
                    comment_id=parent_reply.comment.id,
                    reply_text=reply_text,
                    author=request.user,
                )
                movie_id = parent_reply.comment.movie.id
            else:
                comment = get_object_or_404(Comment, id=comment_id)
                new_reply = CommentReply(
                    comment_id=comment.id,
                    reply_text=reply_text,
                    author=request.user,
                )
                movie_id = comment.movie.id

            new_reply.save()

        messages.success(request, "Reply added successfully!")
        return redirect('show_movie', movie_id=movie_id)

    messages.error(request, "Reply cannot be empty.")
    return redirect(request.META.get("HTTP_REFERER", '/'))


@login_required
@require_http_methods(["POST"])
def vote(request):
    try:
        data = json.loads(request.body.decode('utf-8'))

        comment_id = data.get('comment_id')
        vote_type = data.get('vote_type')

        if not comment_id or not vote_type:
            return JsonResponse({"success": False, "message": "Missing comment_id or vote_type"}, status=400)

        with transaction.atomic():
            if comment_id.startswith("reply-"):
                actual_id = comment_id.replace("reply-", "")
                target_instance = get_object_or_404(CommentReply, id=actual_id)
                vote_filter = {"user": request.user, "reply": target_instance}
            elif comment_id.startswith("comment-"):
                actual_id = comment_id.replace("comment-", "")
                target_instance = get_object_or_404(Comment, id=actual_id)
                vote_filter = {"user": request.user, "comment": target_instance}
            else:
                return JsonResponse({"success": False, "message": "Invalid comment ID"}, status=400)

            existing_vote = Vote.objects.filter(**vote_filter).first()

            if existing_vote:
                if existing_vote.vote_type == vote_type:
                    existing_vote.delete()
                    if vote_type == 'like':
                        target_instance.likes_count = max(0, target_instance.likes_count - 1)
                    elif vote_type == 'dislike':
                        target_instance.dislikes_count = max(0, target_instance.dislikes_count - 1)
                else:
                    if existing_vote.vote_type == 'like':
                        target_instance.likes_count = max(0, target_instance.likes_count - 1)
                    elif existing_vote.vote_type == 'dislike':
                        target_instance.dislikes_count = max(0, target_instance.dislikes_count - 1)

                    existing_vote.vote_type = vote_type
                    existing_vote.save()
                    if vote_type == 'like':
                        target_instance.likes_count += 1
                    elif vote_type == 'dislike':
                        target_instance.dislikes_count += 1
            else:
                Vote.objects.create(vote_type=vote_type, **vote_filter)
                if vote_type == 'like':
                    target_instance.likes_count += 1
                elif vote_type == 'dislike':
                    target_instance.dislikes_count += 1

            target_instance.save()

        return JsonResponse({
            "success": True,
            "likes": target_instance.likes_count,
            "dislikes": target_instance.dislikes_count
        })

    except Exception as e:
        logger.error(f"Error in /vote endpoint: {str(e)}", exc_info=True)
        return JsonResponse({"success": False, "message": "Internal server error"}, status=500)


def load_comments(request, movie_id):
    offset = int(request.GET.get("offset", 0))
    comments = Comment.objects.filter(movie_id=movie_id).select_related('author').order_by("-timestamp")[offset:offset + COMMENTS_PER_PAGE]

    html = render(request, "partials/comment_list.html", {
        "comments": comments,
        "user": request.user,
        "reply_form": ReplyForm(),
        "star_range": range(1, 11),
    }).content.decode("utf-8")
    return JsonResponse({"html": html})


@login_required
@user_passes_test(admin_or_moderator_only)
def add_new_movie(request):
    if request.method == "POST":
        form = FindMovieForm(request.POST)
        if form.is_valid():
            movie_title = form.cleaned_data["title"]
            try:
                response = requests.get(API_URL, params={"api_key": API_KEY, "query": movie_title}, timeout=10)
                response.raise_for_status()
                data = response.json().get("results", [])
                return render(request, "select.html", {"options": data})
            except requests.RequestException as e:
                logger.error(f"Error fetching movies from API: {str(e)}", exc_info=True)
                messages.error(request, "Error connecting to movie database. Please try again.")
                return render(request, "make-movie.html", {"form": form})
    else:
        form = FindMovieForm()
    return render(request, "make-movie.html", {"form": form})


@login_required
@user_passes_test(admin_or_moderator_only)
def find_movie(request, movie_id):
    if not movie_id:
        params = urlencode({"message": "No movie ID provided."})
        return redirect(f"{reverse('error')}?{params}")

    try:
        response = requests.get(
            f"{MOVIE_DB_INFO_URL}/{movie_id}",
            params={"api_key": API_KEY},
            timeout=10
        )
        response.raise_for_status()
        data = response.json()

        credits_response = requests.get(
            f"{MOVIE_DB_INFO_URL}/{movie_id}/credits",
            params={"api_key": API_KEY},
            timeout=10
        )
        credits_response.raise_for_status()
        credits_data = credits_response.json()

        director = ", ".join([crew["name"] for crew in credits_data.get("crew", []) if crew.get("job") == "Director"])
        writers = ", ".join(
            [crew["name"] for crew in credits_data.get("crew", []) if crew.get("job") in ["Writer", "Screenplay"]])
        genres = ", ".join([g["name"] for g in data.get("genres", [])])

        img_url = f"{API_IMG_URL}{data['poster_path']}" if data.get("poster_path") else None

        with transaction.atomic():
            new_movie = Movie(
                title=data.get("title", "Unknown Title"),
                date=data.get("release_date", "").split("-")[0] if data.get("release_date") else None,
                img_url=img_url,
                body=data.get("overview", ""),
                rating=data.get("vote_average"),
                director=director,
                writers=writers,
                genres=genres
            )
            new_movie.save()

        return redirect("edit_movie", movie_id=new_movie.id)

    except requests.RequestException as e:
        logger.error(f"Error fetching movie from API: {str(e)}", exc_info=True)
        params = urlencode({"message": "Error connecting to movie database"})
        return redirect(f"{reverse('error')}?{params}")
    except Exception as e:
        # POPRAWKA: Proper logging
        logger.error(f"Unexpected error in find_movie: {str(e)}", exc_info=True)
        params = urlencode({"message": "An unexpected error occurred"})
        return redirect(f"{reverse('error')}?{params}")


@login_required
@user_passes_test(admin_or_moderator_only)
def edit_movie(request, movie_id):
    movie = get_object_or_404(Movie, id=movie_id)
    if request.method == "POST":
        form = CreateMovieForm(request.POST, instance=movie)
        if form.is_valid():
            with transaction.atomic():
                form.save()
            return redirect("show_movie", movie_id=movie.id)
    else:
        form = CreateMovieForm(instance=movie)
    return render(request, "make-movie.html", {"form": form, "is_edit": True, "current_user": request.user})


@login_required
@user_passes_test(admin_or_moderator_only)
def delete_movie(request, movie_id):
    movie_to_delete = get_object_or_404(Movie, id=movie_id)
    with transaction.atomic():
        movie_to_delete.delete()
    return redirect("get_all_movies")


@login_required
@user_passes_test(admin_or_moderator_only)
def users(request):
    all_users = User.objects.all()
    return render(request, "users.html", {"all_users": all_users, "current_user": request.user})


@login_required
def user_profile(request, user_id):
    profile_owner = get_object_or_404(User, id=user_id)
    comments = Comment.objects.filter(author=profile_owner).select_related('movie')
    replies = CommentReply.objects.filter(author=profile_owner).select_related('comment__movie')

    user_comments = {}
    for comment in comments:
        movie = comment.movie
        user_comments.setdefault(movie, {"comments": [], "replies": {}})
        user_comments[movie]["comments"].append({
            "id": comment.id,
            "text": comment.text,
            "author_id": comment.author.id
        })
        user_comments[movie]["replies"][comment.id] = []

    for reply in replies:
        comment = reply.comment
        movie = comment.movie if comment else None
        if movie:
            user_comments.setdefault(movie, {"comments": [], "replies": {}})
            user_comments[movie]["replies"].setdefault(comment.id, [])
            user_comments[movie]["replies"][comment.id].append({
                "id": reply.id,
                "reply_text": reply.reply_text,
                "author_id": reply.author.id
            })

    return render(request, "user.html", {"profile_owner": profile_owner, "user_comments": user_comments})


@require_POST
@login_required
def delete_comment(request, comment_id):
    comment = Comment.objects.filter(id=comment_id).first()
    if not comment:
        return JsonResponse({"success": False, "message": "Comment not found."}, status=404)

    if not (request.user.id == comment.author.id or request.user.is_admin or request.user.is_moderator):
        return JsonResponse({
            "success": False,
            "message": "You do not have permission to delete this comment."
        }, status=403)

    try:
        with transaction.atomic():
            Vote.objects.filter(comment_id=comment_id).delete()
            CommentReply.objects.filter(comment_id=comment_id).delete()
            comment.delete()
        return JsonResponse({"success": True})
    except Exception as e:
        logger.error(f"Error deleting comment {comment_id}: {str(e)}", exc_info=True)
        return JsonResponse({"success": False, "message": "Error deleting comment"}, status=500)


@require_POST
@login_required
def delete_reply(request, reply_id):
    reply = CommentReply.objects.filter(id=reply_id).first()
    if not reply:
        return JsonResponse({"success": False, "message": "Reply not found."}, status=404)

    if not (request.user.id == reply.author.id or request.user.is_admin or request.user.is_moderator):
        return JsonResponse({
            "success": False,
            "message": "You do not have permission to delete this reply."
        }, status=403)

    try:
        with transaction.atomic():
            reply.delete()
        return JsonResponse({"success": True})
    except Exception as e:
        logger.error(f"Error deleting reply {reply_id}: {str(e)}", exc_info=True)
        return JsonResponse({"success": False, "message": "Error deleting reply"}, status=500)


@require_POST
@login_required
def edit_comment(request, comment_id):
    comment = Comment.objects.filter(id=comment_id).first()
    if not comment:
        return JsonResponse({"success": False, "message": "Comment not found."}, status=404)

    if request.user.id != comment.author.id:
        return JsonResponse({
            "success": False,
            "message": "You can only edit your own comments."
        }, status=403)

    try:
        data = json.loads(request.body.decode('utf-8'))
        new_text = data.get('text', '').strip()

        if not new_text:
            return JsonResponse({"success": False, "message": "Comment cannot be empty."}, status=400)

        with transaction.atomic():
            comment.text = new_text
            comment.save()

        return JsonResponse({"success": True})

    except Exception as e:
        logger.error(f"Error editing comment {comment_id}: {str(e)}", exc_info=True)
        return JsonResponse({"success": False, "message": "Error editing comment"}, status=500)


@require_POST
@login_required
def edit_reply(request, reply_id):
    reply = CommentReply.objects.filter(id=reply_id).first()
    if not reply:
        return JsonResponse({"success": False, "message": "Reply not found."}, status=404)

    if request.user.id != reply.author.id:
        return JsonResponse({
            "success": False,
            "message": "You can only edit your own replies."
        }, status=403)

    try:
        data = json.loads(request.body.decode('utf-8'))
        new_text = data.get('text', '').strip()

        if not new_text:
            return JsonResponse({"success": False, "message": "Reply cannot be empty."}, status=400)

        with transaction.atomic():
            reply.reply_text = new_text
            reply.save()

        return JsonResponse({"success": True})

    except Exception as e:
        logger.error(f"Error editing reply {reply_id}: {str(e)}", exc_info=True)
        return JsonResponse({"success": False, "message": "Error editing reply"}, status=500)


def about(request):
    return render(request, "about.html", {"current_user": request.user})


def seo(request):
    return render(request, "seo.html", {"current_user": request.user})


def error(request, message=None):
    if not message:
        message = request.GET.get("message", "Unknown error")
    return render(request, "error.html", {"message": message})