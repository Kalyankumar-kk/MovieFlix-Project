from django.urls import path
from customer_panel import views


urlpatterns = [
    path('customer_register_page/',views.customer_register_page, name='customer_register'),
    path('customer_login_page/',views.customer_login_page, name='customer_login'),
    path('customer_logout_action/',views.customer_logout_action, name = 'customer_logout'),
    path('customer_login_forgot_password_action',views.customer_login_forgot_password_action, name = 'customer_login_forgot_password_action'),
    path('verify_customer_old_password/', views.verify_customer_old_password, name='verify_customer_old_password'),


    path('customer_dashboard_page/',views.customer_dashboard_page, name = 'customer_dashboard'),
    path('customer_update_profile/', views.customer_update_profile, name='update_profile'),
    path('save_dashboard_language/', views.save_dashboard_language, name='save_dashboard_language'),
    

    path('customer_movie_page/', views.customer_movie_page, name = 'customer_movie'),
    path('customer_movie_player_page/<int:movie_id>/', views.customer_movie_player_page, name='customer_movie_player_page'),

    path('customer_web_series_page/',views.customer_web_series_page, name = 'customer_web_series'),
    path('get_episodes_for_customer/', views.get_episodes_for_edit, name='get_episodes_for_customer'),
    path('customer_series_player_page/<int:series_id>/', views.customer_series_player_page, name='customer_series_player_page'),

    path('customer_profile_settings_page/',views.customer_profile_settings_page, name = "customer_profile_settings"),
    path('customer_change_password_action/', views.customer_change_password_action, name='customer_change_password_action'),
    path('customer_forgot_password_action/', views.customer_forgot_password_action, name='customer_forgot_password_action'),
    
    path('customer_watch_history_page/',views.customer_watch_history_page, name = "customer_watch_history"),
    path('customer_clear_history_action/', views.customer_clear_history_action, name='customer_clear_history'),
    path('customer_delete_history_item/<int:history_id>/', views.customer_delete_history_item, name='customer_delete_history_item'),

    path('customer_liked_videos_page/',views.customer_liked_videos_page, name = "customer_liked_videos"),
    path('customer_toggle_like/', views.customer_toggle_like, name='customer_toggle_like'),
    path('customer_clear_likes/', views.customer_clear_likes_action, name='customer_clear_all_likes'),

    
    path('customer_subscriptions/', views.customer_subscriptions, name='customer_subscriptions'),
    path('customer_process_subscriptions/<str:plan_type>/<int:months>/', views.customer_process_subscriptions, name='customer_process_subscriptions'),
    path('payment_callback/', views.payment_callback, name='payment_callback'),
    path('payment_failed/', views.payment_failed, name='payment_failed'),
    path('cancel_subscription/', views.customer_cancel_subscription, name='customer_cancel_subscription'),

    path('customer_search_page/', views.customer_search_page, name='customer_search'),
    path('api/live_search/', views.live_search_api, name='live_search_api'),


]
    
  
