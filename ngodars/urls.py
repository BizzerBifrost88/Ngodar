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
    path('user-home/food-list/food-search/<str:search_query>/', views.food_search, name='food_search'),
    path('user-home/hall-list/hall-search/<str:search_query>/', views.hall_search, name='hall_search'),
    path('user-home/catering-list/catering-search/<str:search_query>/', views.catering_search, name='catering_search'),
    path('user-home/food-list/food-premise/<int:premise_id>', views.food_premise, name='food_premise'),
    path('user-home/catering-list/catering-premise/<int:premise_id>', views.catering_premise, name='catering_premise'),
    path('user-home/hall-list/hall-premise/<int:premise_id>', views.hall_premise, name='hall_premise'),
    path('user-home/location/', views.user_location, name='user_location'),
    path('user-home/location/add-address/', views.add_address, name='add_address'),
    path('user-home/location/use-address/<int:address_id>/', views.use_address, name='use_address'),
    path('user-home/location/delete-address/<int:address_id>/', views.delete_address, name='delete_address'),    
    path('user-home/catering-list/', views.catering_list, name='catering_list'),
    path('user-home/hall-list/', views.hall_list, name='hall_list'),
    path('user-home/user-profile/', views.user_profile, name='user_profile'),
    path('user-home/receipt/', views.receipt, name='receipt'),
    path('user-home/user-profile/update/', views.user_update, name='user_update'),
    path('user-home/user-profile/update-password/', views.user_update_password, name='user_update_password'),

    # merchant section
    path('user-home/merchant-register/', views.merchant_register, name='merchant_register'),
    path('user-home/merchant-dashboard/', views.merchant_dashboard, name='merchant_dashboard'),
    path('user-home/premise/', views.premise, name='premise'),
    path('user-home/premise/add/', views.add_premise, name='add_premise'),
    path('user-home/premise/update/<int:premise_id>/', views.update_premise, name='update_premise'),
    path('user-home/premise/delete/<int:premise_id>/', views.delete_premise, name='delete_premise'),
] 
