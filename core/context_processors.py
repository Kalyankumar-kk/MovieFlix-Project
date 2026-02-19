# core/context_processors.py
from .models import Notification



def notifications_processor(request):

    from admin_panel.models import AdminRegister
    from customer_panel.models import CustomerRegister
    # 1. Identify which session is active
    if request.session.get('admin_username'):
        current_user = request.session.get('admin_username')
        role = 'admin'
    elif request.session.get('customer_username'):
        current_user = request.session.get('customer_username')
        role = 'customer'
    else:
        # If no user is logged in, show nothing
        return {'notifications': [], 'unread_count': 0}

    # 2. Fetch notifications matching BOTH username AND role
    user_settings = None
    if role == 'admin':
        user_settings = AdminRegister.objects.filter(admin_username=current_user).first()
    else:
        user_settings = CustomerRegister.objects.filter(customer_username=current_user).first()

    # 2. Check the toggle
    if user_settings and not user_settings.notifications_enabled:
        return {'notifications': [], 'unread_count': 0} # Hidden, but DB still has the data!

    # 3. If enabled, show them as usual
    all_notifications = Notification.objects.filter(
        recipient_username=current_user, 
        user_role=role
    ).order_by('-created_at')
    
    # 3. Only count unread items for this specific user/role combination
    unread_count = Notification.objects.filter(
        recipient_username=current_user, 
        user_role=role, 
        is_read=False
    ).count()

    return {
        'notifications': all_notifications,
        'unread_count': unread_count
    }

