from django.urls import path
from admin_panel import views

urlpatterns = [

    path('admin_register_page/',views.admin_register_page, name='admin_register'),
    path('admin_login_page/',views.admin_login_page, name='admin_login'),
    path('admin_logout_action/',views.admin_logout_action, name = 'admin_logout'),
    path('admin_login_forgot_password_action/',views.admin_login_forgot_password_action, name = 'admin_login_forgot_password_action'),
    


    path('admin_dashboard_page/',views.admin_dashboard_page, name = 'admin_dashboard'),
    path('admin_update_profile/', views.admin_update_profile, name='update_profile'),

    path('admin_language_page/',views.admin_language_page, name = 'admin_language'),
    path('add_language/', views.add_language, name='add_language'),
    path('delete_language/<int:lang_id>/', views.delete_language, name='delete_language'),
    path('update_language/<int:lang_id>/', views.update_language, name='update_language'),

    path('admin_genre_page/', views.admin_genre_page, name='admin_genre_page'),
    path('add_genre/', views.add_genre, name='add_genre'),
    path('delete_genre/<int:genre_id>/', views.delete_genre, name='delete_genre'),
    path('update_genre/<int:genre_id>/', views.update_genre, name='update_genre'),

    path('admin_movie_page/', views.admin_movie_page, name='admin_movie_page'),
    path('add_movie_action/', views.add_movie_action, name='add_movie_action'),
    path('delete_movie/<int:movie_id>/', views.delete_movie, name='delete_movie'),
    path('update_movie/<int:movie_id>/', views.update_movie, name='update_movie'),

   

    path('admin_web_series_page/', views.admin_web_series_page, name='admin_webseries'),
    path('add_web_series_action/', views.add_web_series_action, name='add_web_series_action'),
    path('add_season_action/', views.add_season_action, name='add_season_action'),
    path('add_episode_action/', views.add_episode_action, name='add_episode_action'),
    path('get_episodes_for_edit/', views.get_episodes_for_edit, name='get_episodes_for_edit'),
    path('update_series_basic_action/', views.update_series_basic_action, name='update_series_basic_action'),
    path('update_episode_action/', views.update_episode_action, name='update_episode_action'),
    path('update_bulk_episodes_action/', views.update_bulk_episodes_action, name='update_bulk_episodes_action'),
    path('delete_episode_action/', views.delete_episode_action, name='delete_episode_action'),
    path('delete_season_action/', views.delete_season_action, name='delete_season_action'),
    path('define_seasons_action/', views.define_seasons_action, name='define_seasons_action'),
    path('delete_web_series_action/', views.delete_web_series_action, name='delete_web_series_action'),

 
    
    path('admin_profile_settings_page/',views.admin_profile_settings_page, name = 'admin_profile_settings'),
    path('verify_old_password/', views.verify_old_password, name='verify_old_password'),
    path('admin_change_password_action/', views.admin_change_password_action, name='admin_change_password_action'),
    path('admin_forgot_password_action/', views.admin_forgot_password_action, name='admin_forgot_password_action'),

    
    path('admin_subscriptions_page/', views.admin_subscriptions_page, name='admin_subscriptions_page'),
    path('delete_subscription_action/', views.delete_subscription_action, name='delete_subscription_action'),

]