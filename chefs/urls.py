from django.urls import path
from . import views

#URL Configuration
urlpatterns = [path('menus/', views.getMenus),
               path('register/', views.RegisterView.as_view()),
               path('login/', views.LoginView.as_view()),
               path('logout/', views.LogoutView.as_view()),
               path('chef/', views.ChefView.as_view()),
               path('item/', views.ItemView.as_view()),
               path('user/', views.UserView.as_view())]