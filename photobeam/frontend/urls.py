from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),  # Define a view
    path('upload/', views.take_picture, name='upload_picture'),
    path('register/', views.register, name='register'),
    path('profile/', views.profile, name='profile'),
    path('contact/', views.contact, name='contact'),
    path('faq/', views.faq, name='faq'),
    path('about/', views.about, name='about'),
    path('services/', views.services, name='services'),
    path('login/', auth_views.LoginView.as_view(template_name='login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='index'), name='logout'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='password_change.html'), name='password_change'),
    path('password_change_done/', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'), name='password_change_done'),
    path('album/', views.user_album, name='user_album'),
    path("delete_album/<uuid:album_id>/", views.delete_album, name="delete_album"),
    path("delete_image/<int:image_id>/", views.delete_image, name="delete_image"),
    path('create-checkout-session/', views.create_checkout_session, name='create_checkout_session'),
    path('create-album-success/', views.create_album_success, name='create_album_success'),
    path('download_album/<str:album_id>/', views.download_album, name='download_album'),
]