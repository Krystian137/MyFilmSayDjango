from django.urls import path
from . import views

urlpatterns = [
    path('', views.get_all_movies, name='get_all_movies'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('assign_role/<int:user_id>/<str:role>/', views.assign_role, name='assign_role'),
    path('logout/', views.logout_view, name='logout'),
    path('delete_user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('search/', views.search, name='search'),
    path('movie/<int:movie_id>', views.show_movie, name='show_movie'),
    path('reply_comment/<int:comment_id>', views.reply_comment, name='reply_comment'),
    path('vote/', views.vote, name='vote'),
    path("movie/<int:movie_id>/comments/<int:offset>/", views.load_comments, name="load_comments"),
    path("new-movie/", views.add_new_movie, name="add_new_movie"),
    path("find/", views.find_movie, name="find_movie"),
    path("edit-movie/<int:movie_id>/", views.edit_movie, name="edit_movie"),
    path("delete/<int:movie_id>", views.delete_movie, name="delete_movie"),
    path("users", views.users, name="users"),
    path("user/<int:user_id>", views.user_profile, name="user_profile"),
    path("delete_comment/<int:comment_id>", views.delete_comment, name="delete_comment"),
    path("delete_reply/<int:reply_id>", views.delete_reply, name="delete_reply"),
    path("about", views.about, name="about"),
    path("contact", views.contact, name="contact"),
    path("error", views.error, name="error"),
]
