from django.http import JsonResponse
from core.models import Notification
from admin_panel.models import AdminRegister  # Import your user models
from customer_panel.models import CustomerRegister
import json
from django.shortcuts import get_object_or_404
from django.views.decorators.http import require_POST

def mark_notifications_as_read(request):
    if request.method == "POST":
        # Identify the user and their role from the active session
        admin_uname = request.session.get('admin_username')
        cust_uname = request.session.get('customer_username')
        
        if admin_uname:
            # Mark read only for this Admin
            Notification.objects.filter(
                recipient_username=admin_uname, 
                user_role='admin', 
                is_read=False
            ).update(is_read=True)
        elif cust_uname:
            # Mark read only for this Customer
            Notification.objects.filter(
                recipient_username=cust_uname, 
                user_role='customer', 
                is_read=False
            ).update(is_read=True)
            
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)



def clear_notifications(request):
    if request.method == "POST":
        admin_uname = request.session.get('admin_username')
        cust_uname = request.session.get('customer_username')
        
        if admin_uname:
            # Delete only for this specific Admin
            Notification.objects.filter(
                recipient_username=admin_uname, 
                user_role='admin'
            ).delete()
        elif cust_uname:
            # Delete only for this specific Customer
            Notification.objects.filter(
                recipient_username=cust_uname, 
                user_role='customer'
            ).delete()
            
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error'}, status=400)

@require_POST
def delete_single_notification(request):
    try:
        data = json.loads(request.body)
        notification_id = data.get('id')
        
        # Identify current user based on session
        admin_uname = request.session.get('admin_username')
        cust_uname = request.session.get('customer_username')
        
        if admin_uname:
            current_user = admin_uname
            role = 'admin'
        elif cust_uname:
            current_user = cust_uname
            role = 'customer'
        else:
            return JsonResponse({'status': 'error', 'message': 'User not authenticated'}, status=403)
            
        # Verify the notification belongs to this user before deleting
        notification = get_object_or_404(
            Notification, 
            id=notification_id, 
            recipient_username=current_user, 
            user_role=role
        )
        notification.delete()
        
        return JsonResponse({'status': 'success'})
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=400)

def toggle_notifications(request):
    if request.method == "POST":
        admin_uname = request.session.get('admin_username')
        cust_uname = request.session.get('customer_username')

        if admin_uname:
            user = AdminRegister.objects.get(admin_username=admin_uname)
            user.notifications_enabled = not user.notifications_enabled
            user.save()
        elif cust_uname:
            user = CustomerRegister.objects.get(customer_username=cust_uname)
            user.notifications_enabled = not user.notifications_enabled
            user.save()

        return JsonResponse({'status': 'success', 'is_enabled': user.notifications_enabled})