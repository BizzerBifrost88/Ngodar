from django.urls import path
from . import views


urlpatterns = [
    # home section
    path('', views.index, name='index'),
    path('login/', views.login, name='login'),
    path('signup/', views.signup, name='signup'),
    path('logout/', views.logout, name='logout'),
    
    # user section
    path('user-home/', views.user_home, name='user_home'),
    path('user-home/food-list/', views.food_list, name='food_list'),
    path('user-home/catering-list/', views.catering_list, name='catering_list'),
    path('user-home/hall-list/', views.hall_list, name='hall_list'),
    path('user-home/user-profile/', views.user_profile, name='user_profile'),
    path('user-home/merchant-register/', views.merchant_register, name='merchant_register'),
    path('user-home/receipt/', views.receipt, name='receipt'),
] 
