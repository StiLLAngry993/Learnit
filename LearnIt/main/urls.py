from django.urls import path
from . import views

urlpatterns = [
    # Public pages
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('signup/', views.signup_view, name='signup'),

    # Communities
    path('communities/', views.explore_communities, name='explore_communities'),
    path('community/', views.explore_communities, name='community_home'),
    path('community/create/', views.create_community, name='create_community'),
    path('community/<slug:slug>/', views.community_detail, name='community_detail'),
    path('community/<slug:slug>/join/', views.join_community, name='join_community'),
    path('upload/', views.upload_redirect, name='upload_redirect'),

    # Posts inside community
    path('community/<slug:slug>/upload/', views.upload_post, name='upload_post'),
    path('post/<int:post_id>/comment/', views.add_comment, name='add_comment'),
    path('post/<int:post_id>/mark-correct/<int:comment_id>/', views.mark_comment_correct, name='mark_comment_correct'),
    path('post/<int:post_id>/', views.post_detail, name='post_detail'),

    # Profile
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),
    path('profile/<str:username>/', views.user_profile, name='user_profile'),
]