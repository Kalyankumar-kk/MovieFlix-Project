from django.shortcuts import render
from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, redirect
from core.models import Language,Genre,Movie,WatchHistory,LikedVideo
from core.models import WebSeries ,Season, Episode
from .models import CustomerRegister,CustomerSubscription
from django.http import JsonResponse
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.utils import timezone
from django.views.decorators.http import require_POST
from datetime import timedelta
from django.utils import timezone
from django.utils import timezone
from django.contrib.auth.hashers import make_password, check_password
import random
import string
import pytz
import razorpay
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponseBadRequest
import threading
razorpay_client = razorpay.Client(auth=(settings.RAZOR_KEY_ID, settings.RAZOR_KEY_SECRET))
from functools import wraps


def customer_session_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        #  Use  customer session key
        customer_id = request.session.get('customer_id')
        
        if not customer_id:
            # Redirect to  customer login page
            return redirect('/customer_panel/customer_login_page/')

        #  Check timeout for temporary sessions
        is_persistent = request.session.get('is_persistent', False)
        if not is_persistent:
            last_touch = request.session.get('last_touch')
            # 3600 = 1 hour
            if last_touch and (timezone.now().timestamp() - last_touch > 3600):
                request.session.flush()
                return redirect('/customer_panel/customer_login_page/')
        
        #  Update activity timestamp
        request.session['last_touch'] = timezone.now().timestamp()
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view

def customer_register_page(request):
    if request.method == "POST":
       
        fname = request.POST.get('customer_first_name')
        lname = request.POST.get('customer_last_name')
        u_email = request.POST.get('customer_email')
        u_username = request.POST.get('customer_username') 
        u_mobileno = request.POST.get('customer_mobileno')
        u_pwd = request.POST.get('customer_password')
        u_pic = request.FILES.get('customer_profile_pic')

        #  Save it to the Database
        new_customer = CustomerRegister(
            customer_first_name=fname,
            customer_last_name=lname,
            customer_email=u_email,
            customer_username=u_username, # SAVE THE USERNAME HERE
            customer_mobileno=u_mobileno,
            customer_password=make_password(u_pwd),
            customer_profile_pic=u_pic
        )
        try:
           new_customer.save()
        except IntegrityError:
          # Handle the error, e.g., redirect back with a message
         print("Email already exists!")

        # After saving, send them to the login page
        return redirect('/customer_panel/customer_login_page/')
    
    return render(request, 'customer_panel/Internship28-octOR.html')


def customer_login_page(request):
    # Optional: Redirect if already logged in
    if request.session.get('customer_id'):
        return redirect('/customer_panel/customer_dashboard_page/')

    if request.method == "POST":
        username_entered = request.POST.get('customer_entered_username')
        password_entered = request.POST.get('customer_entered_password')
        
        # 1. Capture the checkbox value
        keep_signed_in = request.POST.get('keep_signed_in') 
        
        try:
            customer = CustomerRegister.objects.get(customer_username=username_entered)
            
            if check_password(password_entered, customer.customer_password):
                # 2. Set Basic Session Data
                request.session['customer_id'] = customer.id
                request.session['customer_username'] = customer.customer_username

                # 3. SET EXPIRY LOGIC (Matches your Decorator)
                # Change this part in your views.py
                if keep_signed_in:
                    # Ticked: 14 days in seconds (1209600)
                    request.session.set_expiry(1209600) 
                    request.session['is_persistent'] = True
                else:
                    # Unticked: Session expires when app process stops
                    request.session.set_expiry(0)
                    request.session['is_persistent'] = False
                    request.session['last_touch'] = timezone.now().timestamp()

                return redirect('/customer_panel/customer_dashboard_page/')
            else:
                return render(request, 'customer_panel/Internship28-octOL.html', {'error': 'Invalid Credentials'})
                
        except CustomerRegister.DoesNotExist:
            return render(request, 'customer_panel/Internship28-octOL.html', {'error': 'Invalid Credentials'})
    
    return render(request, 'customer_panel/Internship28-octOL.html')

def customer_logout_action(request):
    # This deletes all session data (username, id, etc.)
    request.session.flush() 
    # Now that the session is gone, redirecting to login will actually work
    return redirect('/customer_panel/customer_login_page/')

def customer_login_forgot_password_action(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            customer = CustomerRegister.objects.get(customer_email=email)
            
            # Generate a random temporary password
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            
            # Hash and save it
            customer.customer_password = make_password(temp_password)
            customer.save()
            
            # ⭐ PROFESSIONAL HTML EMAIL ⭐
            ist = pytz.timezone('Asia/Kolkata')
            now_ist = timezone.now().astimezone(ist)
            
            subject = '🔐 Password Reset - Movieflix Account'
            
            html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f4; font-family: Arial, sans-serif;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td align="center" style="padding: 40px 0;">
                <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    
                    <!-- Header with Logo/Brand -->
                    <tr>
                        <td style="padding: 40px 40px 30px 40px; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                            <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: bold;">MOVIEFLIX</h1>
                        </td>
                    </tr>
                    
                    <!-- Main Content -->
                    <tr>
                        <td style="padding: 40px;">
                            <h2 style="margin: 0 0 20px 0; color: #333333; font-size: 24px;">Password Reset Request</h2>
                            
                            <p style="margin: 0 0 20px 0; color: #666666; font-size: 16px; line-height: 1.5;">
                                Hello <strong>{customer.customer_first_name} {customer.customer_last_name}</strong>,
                            </p>
                            
                            <p style="margin: 0 0 30px 0; color: #666666; font-size: 16px; line-height: 1.5;">
                                We received a request to reset your password. Your temporary password has been generated successfully.
                            </p>
                            
                            <!-- Temporary Password Card -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 30px;">
                                <tr>
                                    <td style="padding: 25px;">
                                        <h3 style="margin: 0 0 15px 0; color: #333333; font-size: 18px;">Your Temporary Password</h3>
                                        
                                        <div style="background-color: #ffffff; padding: 15px; border-radius: 6px; border-left: 4px solid #667eea; margin-bottom: 15px;">
                                            <p style="margin: 0; font-family: 'Courier New', monospace; font-size: 24px; font-weight: bold; color: #667eea; letter-spacing: 2px;">
                                                {temp_password}
                                            </p>
                                        </div>
                                        
                                        <p style="margin: 0; color: #666666; font-size: 14px; line-height: 1.5;">
                                            <strong style="color: #e74c3c;">⚠️ Important Security Notice:</strong><br>
                                            Please change this password immediately after logging in from your profile settings.
                                        </p>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Account Details -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 30px;">
                                <tr>
                                    <td style="padding: 25px;">
                                        <h3 style="margin: 0 0 15px 0; color: #333333; font-size: 18px;">Account Information</h3>
                                        
                                        <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                            <tr>
                                                <td style="padding: 8px 0; color: #666666; font-size: 14px; width: 40%;">Email</td>
                                                <td style="padding: 8px 0; color: #333333; font-size: 14px; font-weight: bold;">{customer.customer_email}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0; border-top: 1px solid #dee2e6; color: #666666; font-size: 14px;">Username</td>
                                                <td style="padding: 8px 0; border-top: 1px solid #dee2e6; color: #333333; font-size: 14px; font-weight: bold;">{customer.customer_username}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0; border-top: 1px solid #dee2e6; color: #666666; font-size: 14px;">Reset Time</td>
                                                <td style="padding: 8px 0; border-top: 1px solid #dee2e6; color: #333333; font-size: 14px;">{now_ist.strftime('%d %B %Y, %I:%M %p IST')}</td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Instructions -->
                            <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
                                <p style="margin: 0; color: #856404; font-size: 14px; line-height: 1.6;">
                                    <strong>Next Steps:</strong><br>
                                    1. Login to your account using the temporary password above<br>
                                    2. Navigate to Profile Settings<br>
                                    3. Change your password to something secure and memorable
                                </p>
                            </div>
                            
                            <p style="margin: 0 0 10px 0; color: #666666; font-size: 14px; line-height: 1.5;">
                                If you didn't request this password reset, please contact our support team immediately.
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px 40px; background-color: #f8f9fa; text-align: center;">
                            <p style="margin: 0; color: #999999; font-size: 13px;">
                                Best regards,<br>
                                <strong>MovieFlix Team</strong>
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
            
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]
            
            send_mail(
                subject,
                '',  # Plain text version (empty, HTML takes priority)
                email_from,
                recipient_list,
                fail_silently=False,
                html_message=html_message  # HTML email content
            )
            
            messages.success(request, f"✅ A temporary password has been sent to {email}.")
            
        except CustomerRegister.DoesNotExist:
            messages.error(request, "This email is not registered in our customer database.")
        except Exception as e:
            messages.error(request, f"Connection Error: {e}")
    
    return redirect('customer_login')




@customer_session_required
def customer_dashboard_page(request):
    customer_id = request.session.get('customer_id')
    customer = CustomerRegister.objects.get(id=customer_id)

    languages = Language.objects.all()
    genres = Genre.objects.all()

    # Get the key we just saved above
    active_lang_id = request.session.get('dashboard_pref_lang') 

    current_sub = CustomerSubscription.objects.filter(customer=customer, is_active=True).first()
    if current_sub and current_sub.expiry_date < timezone.now():
        current_sub = None
    


    return render(request, 'customer_panel/Internship4-octOD.html', {
        'customer': customer,
        'languages': languages,
        'genres': genres,
        'active_lang_id': active_lang_id, # Pass it as active_lang_id for cleaner HTML
        'current_sub': current_sub,
        
    })

# views.py
def save_dashboard_language(request):
    lang_id = request.GET.get('lang_id')
    
    if lang_id == 'clear':
        if 'dashboard_pref_lang' in request.session:
            del request.session['dashboard_pref_lang'] # Clear the correct key
        return JsonResponse({'status': 'success', 'message': 'Filter cleared'})
        
    if lang_id:
        # Save to the correct key used by other pages
        request.session['dashboard_pref_lang'] = lang_id 
        return JsonResponse({'status': 'success'})
        
    return JsonResponse({'status': 'failed'}, status=400)


def customer_update_profile(request):
    if request.method == "POST":

        customer_id = request.session.get('customer_id')
        customer = CustomerRegister.objects.get(id=customer_id)

        # Update text fields
        customer.customer_first_name = request.POST.get('customer_modal_first_name')
        customer.customer_last_name = request.POST.get('customer_modal_last_name')
        customer.customer_email = request.POST.get('customer_modal_email')
        customer.customer_mobileno = request.POST.get('customer_modal_mobileno')
        
        # SAVE THE USERNAME HERE
        customer.customer_username = request.POST.get('customer_modal_username')

        # SAFELY UPDATE PROFILE PIC
        new_pic = request.FILES.get('customer_profile_pic')
        if new_pic: # Only updates if you actually chose a new file
            customer.customer_profile_pic = new_pic

        customer.save()
        # DYNAMIC REDIRECT: 
        # HTTP_REFERER is the URL the user came from.
        # We use 'customer_profile_settings' as a backup just in case referer is missing.
        return redirect(request.META.get('HTTP_REFERER', 'customer_profile_settings'))
    

@customer_session_required
def customer_movie_page(request):
    customer_id = request.session.get('customer_id')
    customer = CustomerRegister.objects.get(id=customer_id)
    customer_uname = request.session.get('customer_username')

    # 1. Get the manual filter from the URL
    manual_lang = request.GET.get('language')
    selected_genre = request.GET.get('genre')

    # 2. Logic to decide which language to show
    if manual_lang is not None:
        # If the user touched the dropdown (even to select "All"), use that
        selected_lang = manual_lang
        # Important: Update the session so the dashboard preference changes to the new choice
        request.session['dashboard_pref_lang'] = manual_lang
    else:
        # User just opened the page for the first time, use Dashboard preference
        selected_lang = request.session.get('dashboard_pref_lang', "")

    # YOU NEED THIS ON EVERY PAGE:
    current_sub = CustomerSubscription.objects.filter(customer=customer, is_active=True).first()
    if current_sub and current_sub.expiry_date < timezone.now():
        current_sub = None

    # 4. CHECK FOR ACTIVE SUBSCRIPTION 
    subscription = CustomerSubscription.objects.filter(customer=customer, is_active=True).first()
    
    is_subscribed = False
    if subscription:
        if subscription.expiry_date > timezone.now():
            is_subscribed = True
        else:
            # Optional: Mark it inactive in the background if it's expired
            subscription.is_active = False
            subscription.save()

    # 3. Filtering Logic
    movies = Movie.objects.all().order_by('-id')
    if selected_lang != "":
        movies = movies.filter(movie_language_id=selected_lang)
    if selected_genre:
        movies = movies.filter(movie_genre_id=selected_genre)

    languages = Language.objects.all()
    genres = Genre.objects.all()

    return render(request, 'customer_panel/Internship13-novOM.html', {
        'customer': customer,
        'movies': movies,
        'languages': languages,
        'genres': genres,
        'selected_lang': selected_lang,
        'selected_genre': selected_genre,
        'liked_movie_ids': list(LikedVideo.objects.filter(customer_username=customer_uname, movie__isnull=False).values_list('movie_id', flat=True)),
        'is_subscribed': is_subscribed,
        'current_sub': current_sub
    })



# customer_panel/views.py
@customer_session_required
def customer_web_series_page(request):
    customer_id = request.session.get('customer_id')
    customer = CustomerRegister.objects.get(id=customer_id)
    customer_uname = request.session.get('customer_username')

    # 1. Get filter IDs from the URL
    url_lang = request.GET.get('language')
    genre_id = request.GET.get('genre')

    # --- SESSION LOGIC START ---
    # Check if 'language' is explicitly in the GET parameters (even if empty)
    if 'language' in request.GET:
        selected_lang = url_lang
        # Update session with the user's manual choice (or clear it if url_lang is "")
        request.session['dashboard_pref_lang'] = url_lang
    else:
        # User just arrived, use the preference saved from the dashboard
        selected_lang = request.session.get('dashboard_pref_lang', "")
    # --- SESSION LOGIC END ---

    # 2. Start with all web series
    series_list = WebSeries.objects.all().order_by('-created_at')

    # 3. Apply filters 

    if selected_lang:
        series_list = series_list.filter(series_language_id=selected_lang)
        
    if genre_id:
        series_list = series_list.filter(series_genre_id=genre_id)

    # 4. Fetch all records for the dropdowns
    languages = Language.objects.all()
    genres = Genre.objects.all()

    # YOU NEED THIS ON EVERY PAGE:
    current_sub = CustomerSubscription.objects.filter(customer=customer, is_active=True).first()
    if current_sub and current_sub.expiry_date < timezone.now():
        current_sub = None


    # 4. CHECK FOR ACTIVE SUBSCRIPTION 
    subscription = CustomerSubscription.objects.filter(customer=customer, is_active=True).first()
    
    is_subscribed = False
    if subscription:
        if subscription.expiry_date > timezone.now():
            is_subscribed = True
        else:
            # Optional: Mark it inactive in the background if it's expired
            subscription.is_active = False
            subscription.save()

    liked_episode_ids = list(LikedVideo.objects.filter(
        customer_username=customer_uname, 
        episode__isnull=False
    ).values_list('episode_id', flat=True))

    return render(request, 'customer_panel/Internship6-decOW.html', {
        'all_series': series_list,
        'customer': customer,
        'languages': languages,
        'genres': genres,
        'selected_lang': selected_lang, # Pass the resolved language back to the template
        'selected_genre': genre_id,
        'liked_episode_ids': liked_episode_ids,
        'is_subscribed': is_subscribed,
        'current_sub': current_sub
    })





def get_episodes_for_edit(request):
    series_id = request.GET.get('series_id')
    season_id = request.GET.get('season_id')
    
    # Using select_related('season') is more efficient as it fetches season data in the same query
    episodes = Episode.objects.filter(
        series_id=series_id, 
        season_id=season_id
    )
    
    episode_list = []
    for ep in episodes:
        episode_list.append({
            'id': ep.id,
            'title': ep.episode_title,
            'url': ep.get_embed_url, # Check if your model field is video_url or episode_video_url
            'release_date': ep.episode_release_date.strftime('%Y-%m-%d') if ep.episode_release_date else '',
            'season_name': ep.season.season_name if ep.season else "S1",
            
            # 1. Current Episode Banner
            'episode_banner_url': ep.episode_banner.url if ep.episode_banner else None,
            
            # 2. Add Season Banner (accessed via the relationship)
            'season_banner_url': ep.season.season_banner.url if ep.season and ep.season.season_banner else None 
        })
        
    return JsonResponse({'episodes': episode_list})




def customer_profile_settings_page(request):
    customer_id = request.session.get('customer_id')
    customer = CustomerRegister.objects.get(id=customer_id)
    # YOU NEED THIS ON EVERY PAGE:
    current_sub = CustomerSubscription.objects.filter(customer=customer, is_active=True).first()
    if current_sub and current_sub.expiry_date < timezone.now():
        current_sub = None



    return render(request, 'customer_panel/Internship5-decOP.html', {
        'customer': customer, # Pass the customer object here
        'current_sub': current_sub,
        
    })


def verify_customer_old_password(request):
    """AJAX endpoint to verify customer old password"""
    if request.method == "POST":
        customer_id = request.session.get('customer_id')
        old_password = request.POST.get('old_password')
        
        try:
            customer = CustomerRegister.objects.get(id=customer_id)
            # Use check_password to verify against hashed version
            if check_password(old_password, customer.customer_password):
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'failed', 'message': 'Incorrect password'})
        except CustomerRegister.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Customer not found'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})



def customer_change_password_action(request):
    if request.method == "POST":
        customer_id = request.session.get('customer_id')
        old_pwd = request.POST.get('old_password')
        new_pwd = request.POST.get('new_password')
        confirm_pwd = request.POST.get('confirm_new_password')
        
        customer = get_object_or_404(CustomerRegister, id=customer_id)
        
        # Verify old password with check_password
        if check_password(old_pwd, customer.customer_password):
            if new_pwd == confirm_pwd:
                customer.customer_password = make_password(new_pwd)  # Hash new password
                customer.save()
                messages.success(request, "Password updated successfully!")
            else:
                messages.error(request, "New passwords did not match.")
        else:
            messages.error(request, "Incorrect old password.")
    
    return redirect('customer_profile_settings')



def customer_forgot_password_action(request):
    """Same logic but redirects to profile settings"""
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            customer = CustomerRegister.objects.get(customer_email=email)
            
            # Generate a random temporary password
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
            
            # Hash and save it
            customer.customer_password = make_password(temp_password)
            customer.save()
            
            # ⭐ PROFESSIONAL HTML EMAIL ⭐
            ist = pytz.timezone('Asia/Kolkata')
            now_ist = timezone.now().astimezone(ist)
            
            subject = '🔐 Password Reset - Movieflix Account'
            
            html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f4; font-family: Arial, sans-serif;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td align="center" style="padding: 40px 0;">
                <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    
                    <!-- Header with Logo/Brand -->
                    <tr>
                        <td style="padding: 40px 40px 30px 40px; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                            <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: bold;">MOVIEFLIX</h1>
                        </td>
                    </tr>
                    
                    <!-- Main Content -->
                    <tr>
                        <td style="padding: 40px;">
                            <h2 style="margin: 0 0 20px 0; color: #333333; font-size: 24px;">Password Reset Request</h2>
                            
                            <p style="margin: 0 0 20px 0; color: #666666; font-size: 16px; line-height: 1.5;">
                                Hello <strong>{customer.customer_first_name} {customer.customer_last_name}</strong>,
                            </p>
                            
                            <p style="margin: 0 0 30px 0; color: #666666; font-size: 16px; line-height: 1.5;">
                                We received a request to reset your password. Your temporary password has been generated successfully.
                            </p>
                            
                            <!-- Temporary Password Card -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 30px;">
                                <tr>
                                    <td style="padding: 25px;">
                                        <h3 style="margin: 0 0 15px 0; color: #333333; font-size: 18px;">Your Temporary Password</h3>
                                        
                                        <div style="background-color: #ffffff; padding: 15px; border-radius: 6px; border-left: 4px solid #667eea; margin-bottom: 15px;">
                                            <p style="margin: 0; font-family: 'Courier New', monospace; font-size: 24px; font-weight: bold; color: #667eea; letter-spacing: 2px;">
                                                {temp_password}
                                            </p>
                                        </div>
                                        
                                        <p style="margin: 0; color: #666666; font-size: 14px; line-height: 1.5;">
                                            <strong style="color: #e74c3c;">⚠️ Important Security Notice:</strong><br>
                                            Please change this password immediately after logging in from your profile settings.
                                        </p>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Account Details -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 30px;">
                                <tr>
                                    <td style="padding: 25px;">
                                        <h3 style="margin: 0 0 15px 0; color: #333333; font-size: 18px;">Account Information</h3>
                                        
                                        <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                            <tr>
                                                <td style="padding: 8px 0; color: #666666; font-size: 14px; width: 40%;">Email</td>
                                                <td style="padding: 8px 0; color: #333333; font-size: 14px; font-weight: bold;">{customer.customer_email}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0; border-top: 1px solid #dee2e6; color: #666666; font-size: 14px;">Username</td>
                                                <td style="padding: 8px 0; border-top: 1px solid #dee2e6; color: #333333; font-size: 14px; font-weight: bold;">{customer.customer_username}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0; border-top: 1px solid #dee2e6; color: #666666; font-size: 14px;">Reset Time</td>
                                                <td style="padding: 8px 0; border-top: 1px solid #dee2e6; color: #333333; font-size: 14px;">{now_ist.strftime('%d %B %Y, %I:%M %p IST')}</td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Instructions -->
                            <div style="background-color: #fff3cd; border-left: 4px solid #ffc107; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
                                <p style="margin: 0; color: #856404; font-size: 14px; line-height: 1.6;">
                                    <strong>Next Steps:</strong><br>
                                    1. Login to your account using the temporary password above<br>
                                    2. Navigate to Profile Settings<br>
                                    3. Change your password to something secure and memorable
                                </p>
                            </div>
                            
                            <p style="margin: 0 0 10px 0; color: #666666; font-size: 14px; line-height: 1.5;">
                                If you didn't request this password reset, please contact our support team immediately.
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px 40px; background-color: #f8f9fa; text-align: center;">
                            <p style="margin: 0; color: #999999; font-size: 13px;">
                                Best regards,<br>
                                <strong>MovieFlix Team</strong>
                            </p>
                        </td>
                    </tr>
                    
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
            
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [email]
            
            send_mail(
                subject,
                '',  # Plain text version (empty, HTML takes priority)
                email_from,
                recipient_list,
                fail_silently=False,
                html_message=html_message  # HTML email content
            )
            
            messages.success(request, f"✅ A temporary password has been sent to {email}.")
            
        except CustomerRegister.DoesNotExist:
            messages.error(request, "This email is not registered in our customer database.")
        except Exception as e:
            messages.error(request, f"Connection Error: {e}")
    
    return redirect('customer_profile_settings')


# -------------
@customer_session_required
def customer_watch_history_page(request):
    customer_id = request.session.get('customer_id')
    customer = CustomerRegister.objects.get(id=customer_id)
    customer_uname = request.session.get('customer_username')

    # YOU NEED THIS ON EVERY PAGE:
    current_sub = CustomerSubscription.objects.filter(customer=customer, is_active=True).first()
    if current_sub and current_sub.expiry_date < timezone.now():
        current_sub = None
    
    # Get the customer object for the sidebar/header
    customer = CustomerRegister.objects.get(id=customer_id)

    # 2. PREMIUM GATE: If not premium, redirect to subscriptions or dashboard
    if not current_sub or current_sub.plan_type != 'premium' or current_sub.expiry_date < timezone.now():
    
        return redirect('customer_subscriptions') # Or redirect to dashboard

    
    
    # Fetch all history for this user
    history_items = WatchHistory.objects.filter(customer_username=customer_uname).order_by('-watched_at')

    return render(request, "customer_panel/Internship26-decOWH.html", {
        'customer': customer,
        'history_items': history_items,
        'current_sub': current_sub
    })



@require_POST
def customer_clear_history_action(request):
    customer_uname = request.session.get('customer_username')
    if customer_uname:
        # This is the command that clears the whole table for this user
        WatchHistory.objects.filter(customer_username=customer_uname).delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Authentication failed'}, status=400)




def customer_delete_history_item(request, history_id):
    customer_uname = request.session.get('customer_username')
    
    # Ensure the history item belongs to the logged-in user before deleting
    history_item = get_object_or_404(WatchHistory, id=history_id, customer_username=customer_uname)
    history_item.delete()
    
    return JsonResponse({'status': 'success'})

# ---
@customer_session_required
def customer_liked_videos_page(request):
    customer_id = request.session.get('customer_id')
    customer = CustomerRegister.objects.get(id=customer_id)
    customer_uname = request.session.get('customer_username')

    current_sub = CustomerSubscription.objects.filter(customer=customer, is_active=True).first()
    
    current_sub = CustomerSubscription.objects.filter(customer=customer, is_active=True).first()
    if current_sub and current_sub.expiry_date < timezone.now():
        current_sub = None

    # 2. PREMIUM GATE: Block access for non-premium
    if not current_sub or current_sub.plan_type != 'premium' or current_sub.expiry_date < timezone.now():
        return redirect('customer_dashboard_page')

    # Fetch liked movies and series
    liked_items = LikedVideo.objects.filter(customer_username=customer_uname).order_by('-liked_at')

    return render(request, "customer_panel/Internship26-decOLV.html", {
        'customer': customer,
        'liked_items': liked_items,
        'current_sub': current_sub,
    })

@require_POST
def customer_toggle_like(request):
    customer_uname = request.session.get('customer_username')
    
    # ADD THIS SAFETY CHECK
    if not customer_uname:
        return JsonResponse({'status': 'error', 'message': 'Please log in'}, status=401)
    
    series_id = request.POST.get('seriesid')
    season_id = request.POST.get('seasonid')
    episode_id = request.POST.get('episodeid')
    movie_id = request.POST.get('movieid')
    
    series = None
    season = None
    movie = None
    episode = None
    
    if movie_id:
        movie = get_object_or_404(Movie, id=movie_id)
    elif series_id:
        series = get_object_or_404(WebSeries, id=series_id)
    
    # ADD THIS CODE - Fetch season and episode objects
    if season_id and season_id.strip():
        season = get_object_or_404(Season, id=season_id)
    if episode_id and episode_id.strip():
        episode = get_object_or_404(Episode, id=episode_id)
    
    # Check for existing like with ALL fields
    like_query = LikedVideo.objects.filter(
        customer_username=customer_uname,
        web_series=series,
        season=season,
        episode=episode,
        movie=movie
    )
    
    if like_query.exists():
        like_query.delete()
        is_liked = False
    else:
        LikedVideo.objects.create(
            customer_username=customer_uname,
            web_series=series,
            season=season,
            episode=episode,
            movie=movie
        )
        is_liked = True
    
    return JsonResponse({'status': 'success', 'isliked': is_liked})




@require_POST
def customer_clear_likes_action(request):
    customer_uname = request.session.get('customer_username')
    if customer_uname:
        # This deletes all LikedVideo records for this user
        LikedVideo.objects.filter(customer_username=customer_uname).delete()
        return JsonResponse({'status': 'success'})
    return JsonResponse({'status': 'error', 'message': 'Authentication failed'}, status=400)


# Updated function in views.py
@customer_session_required
def customer_movie_player_page(request, movie_id):
    # 1. Get IDs from session
    customer_id = request.session.get('customer_id')
    customer_uname = request.session.get('customer_username')

    # 2. Safety check: ensure logged in
    if not customer_id:
        return redirect('customer_login')

    # 3. Fetch objects
    movie = get_object_or_404(Movie, id=movie_id)
    customer = get_object_or_404(CustomerRegister, id=customer_id)

    # YOU NEED THIS ON EVERY PAGE:
    current_sub = CustomerSubscription.objects.filter(customer=customer, is_active=True).first()
    if current_sub and current_sub.expiry_date < timezone.now():
        current_sub = None

    # 4. CHECK FOR ACTIVE SUBSCRIPTION 
    subscription = CustomerSubscription.objects.filter(customer=customer, is_active=True).first()

    is_subscribed = False
    if subscription:
        if subscription.expiry_date > timezone.now():
            is_subscribed = True
        else:
            # Optional: Mark it inactive in the background if it's expired
            subscription.is_active = False
            subscription.save()


    # Only save to WatchHistory if the user is Premium
    current_sub = CustomerSubscription.objects.filter(customer=customer, is_active=True).first()
    if current_sub and current_sub.plan_type == 'premium' and current_sub.expiry_date > timezone.now():
        WatchHistory.objects.update_or_create(
            customer_username=customer_uname,
            movie=movie,
            defaults={'watched_at': timezone.now()}
        )

    is_liked = LikedVideo.objects.filter(customer_username=customer_uname, movie=movie).exists()

    languages = Language.objects.all()
    genres = Genre.objects.all()

    return render(request, 'customer_panel/Internship30-decOMVP.html', {
        'movie': movie,
        'customer': customer,
        'is_liked': is_liked,
        'is_subscribed': is_subscribed,
        'current_sub': current_sub,
        'languages': languages,
        'genres': genres
        
    })


@customer_session_required
def customer_series_player_page(request, series_id):
    customer_id = request.session.get('customer_id')
    customer = get_object_or_404(CustomerRegister, id=customer_id)
    customer_uname = request.session.get('customer_username')

    series = get_object_or_404(WebSeries, id=series_id)
    seasons = series.seasons_list.all().prefetch_related('season_episodes').order_by('season_order')

    # YOU NEED THIS ON EVERY PAGE:
    current_sub = CustomerSubscription.objects.filter(customer=customer, is_active=True).first()
    if current_sub and current_sub.expiry_date < timezone.now():
        current_sub = None
    # Inside your player view in views.py
    subscription = CustomerSubscription.objects.filter(customer=customer, is_active=True).first()

    # Check if subscription exists AND if it is not expired
    is_subscribed = False
    if subscription:
        if subscription.expiry_date > timezone.now():
            is_subscribed = True
        else:
            if subscription.is_active:
                subscription.is_active = False
                subscription.save()

    # Now pass is_subscribed to your template
    
    play_episode_id = request.GET.get('play')
    selected_episode = None
    selected_season_id = None 

    # 1. Identify the episode and update Watch History
    if play_episode_id:
        selected_episode = get_object_or_404(Episode, id=play_episode_id)
        selected_season_id = selected_episode.season.id

    # Only save to WatchHistory if user is Premium AND they have actually clicked an episode
    if current_sub and current_sub.plan_type == 'premium' and current_sub.expiry_date > timezone.now():
        if selected_episode:  # Add this check to prevent crash on landing
            WatchHistory.objects.update_or_create(
                customer_username=customer_uname,
                episode=selected_episode,
                web_series=series, # Specificity prevents finding duplicates of other series
                defaults={'watched_at': timezone.now()}
            )
    

    # 2. Check if the SERIES itself is liked (Banner Icon)
    # This specifically looks for the series where BOTH episode AND season are NULL
    is_series_liked = LikedVideo.objects.filter(
        customer_username=customer_uname, 
        web_series=series,
        episode__isnull=True,
        season__isnull=True  # NEW: Make sure it's series-level only
    ).exists()

     # NEW: Check if the current SEASON is liked
    is_season_liked = False

    # Determine which season to check
    if selected_episode:
        # If playing an episode, check that episode's season
        current_season = selected_episode.season
    else:
        # If on landing page, check the first season (default displayed)
        current_season = seasons.first() if seasons.exists() else None

    # Now check if that season is liked
    if current_season:
        is_season_liked = LikedVideo.objects.filter(
            customer_username=customer_uname,
            web_series=series,
            season=current_season,
            episode__isnull=True  # Season-level like, not episode
        ).exists()


    # 3. Check if the CURRENT EPISODE is liked (Player Icon)
    is_episode_liked = False
    if selected_episode:
        is_episode_liked = LikedVideo.objects.filter(
            customer_username=customer_uname, 
            episode=selected_episode
        ).exists()

   # Get list of liked season IDs (same pattern as liked episodes)
    liked_season_ids = list(LikedVideo.objects.filter(
        customer_username=customer_uname,
        web_series=series,
        season__isnull=False,
        episode__isnull=True
    ).values_list('season_id', flat=True))

    languages = Language.objects.all()
    genres = Genre.objects.all()


    # --- CORRECTED LOGIC FOR NEXT EPISODE ---
# --- CORRECTED LOGIC FOR NEXT EPISODE ---
    next_episode = None
    is_new_season = False

    if selected_episode:  # Only look for a Next Episode if the user is actually watching one
        # 1. Try to find the next episode in the CURRENT season
        next_episode = Episode.objects.filter(
            season=selected_episode.season,
            episode_number__gt=selected_episode.episode_number
        ).order_by('episode_number').first()
        
        # 2. ONLY look for next season if there's NO next episode in current season
        if not next_episode:  # ← THIS IS THE CRITICAL FIX!
            next_season = series.seasons_list.filter(
                season_order__gt=selected_episode.season.season_order
            ).order_by('season_order').first()
            
            if next_season:
                next_episode = next_season.season_episodes.all().order_by('episode_number').first()
                is_new_season = True

    # // to send season id when redirecting form watch historyand liked videos
    episode_id = request.GET.get('play')
    target_season_id = None

    if episode_id:
        # Get the episode and its associated season ID
        episode = get_object_or_404(Episode, id=episode_id)
        target_season_id = episode.season.id

    # 4. Pass both separate booleans to the template
    return render(request, 'customer_panel/Internship30-decOWVP.html', {
    'series': series,
    'seasons': seasons,
    'customer': customer,
    'selected_episode': selected_episode,
    'selected_season_id': selected_season_id,
    'serverSeasonId': target_season_id,
    'is_series_liked': is_series_liked,
    'is_season_liked': is_season_liked,
    'liked_season_ids': liked_season_ids,
    'is_episode_liked': is_episode_liked,
    'next_episode': next_episode,
    'is_new_season': is_new_season,
    'is_subscribed': is_subscribed,
    'current_sub': current_sub,
    'languages': languages,
    'genres': genres,
})


#monitization
@customer_session_required
def customer_subscriptions(request):
    customer_id = request.session.get('customer_id')
    customer = get_object_or_404(CustomerRegister, id=customer_id)
    
    # Fetch the active subscription
    current_sub = CustomerSubscription.objects.filter(customer=customer, is_active=True).first()
    
    time_left = None # Using a dictionary to hold precise units
    
    if current_sub and current_sub.expiry_date > timezone.now():
        # Get the full difference object
        diff = current_sub.expiry_date - timezone.now()
        
        # Logic to extract Days, Hours, and Minutes
        days = diff.days
        hours, remainder = divmod(diff.seconds, 3600)
        minutes, _ = divmod(remainder, 60)
        
        time_left = {
            'days': days,
            'hours': hours,
            'minutes': minutes
        }
    else:
        current_sub = None 

    return render(request, 'customer_panel/Subscriptions.html', {
        'customer': customer,
        'current_sub': current_sub,
        'time_left': time_left  # Pass the new dictionary
    })

def customer_process_subscriptions(request, plan_type, months):
    """Step 1: User clicked Get Started → create Razorpay order and show payment page"""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        return redirect('customer_login')
    
    customer = get_object_or_404(CustomerRegister, id=customer_id)
    
    # Convert months to int
    duration = int(months)
    
    # Simple pricing (in paise)
    pricing = {
        'basic': {1: 9900, 3: 24900},      # ₹99, ₹249
        'premium': {1: 19900, 3: 49900},   # ₹199, ₹499
    }
    amount = pricing[plan_type][duration]
    
    #  GENERATE CUSTOM RECEIPT ID - NEW FORMAT 
    ist = pytz.timezone('Asia/Kolkata')
    now_ist = timezone.now().astimezone(ist)
    
    # Format date and time separately
    date_part = now_ist.strftime('%Y%m%d')      # 20260119
    time_part = now_ist.strftime('%H%M')      # 2225
    
    # Generate random 6-character alphanumeric ID
    random_id = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    
    # Clean username: replace spaces with underscores
    clean_username = customer.customer_username.replace(' ', '_')
    
    # Build custom receipt: MF_(username)_(date)_(time)_(randomID)
    custom_receipt = f"MF_{clean_username}_{date_part}_{time_part}_{random_id}"
    
    # Ensure it's within 40 character limit (Razorpay's max)
    if len(custom_receipt) > 40:
        custom_receipt = custom_receipt[:40]
    
    # Create Razorpay order WITH custom receipt
    razorpay_order = razorpay_client.order.create({
        'amount': amount,
        'currency': 'INR',
        'payment_capture': '1',
        'receipt': custom_receipt,  # Custom receipt
    })
    
    razorpay_order_id = razorpay_order['id']
    
    # Store temporary info in session (we'll need it after payment)
    request.session['pending_plan_type'] = plan_type
    request.session['pending_duration'] = duration
    request.session['pending_amount'] = amount
    request.session['pending_order_id'] = razorpay_order_id
    request.session['pending_custom_receipt'] = custom_receipt  # ADD THIS LINE
    
    context = {
        'customer': customer,
        'razorpay_key_id': settings.RAZOR_KEY_ID,
        'razorpay_order_id': razorpay_order_id,
        'amount': amount,
        'currency': 'INR',
        'plan_type': plan_type.title(),
        'duration': duration,
        'customer_name': f"{customer.customer_first_name} {customer.customer_last_name}",
        'customer_email': customer.customer_email,
        'customer_phone': customer.customer_mobileno,
    }
    
    return render(request, 'customer_panel/payment_page.html', context)




  

@csrf_exempt
def payment_callback(request):
    """Secure payment callback - activates subscription and redirects immediately"""
    if request.method != "POST":
        return HttpResponseBadRequest("Invalid method")
    
    # Get payment details from Razorpay
    payment_id = request.POST.get('razorpay_payment_id')
    order_id = request.POST.get('razorpay_order_id')
    signature = request.POST.get('razorpay_signature')
    
    # Security check: Verify the payment signature
    params_dict = {
        'razorpay_order_id': order_id,
        'razorpay_payment_id': payment_id,
        'razorpay_signature': signature,
    }
    
    try:
        razorpay_client.utility.verify_payment_signature(params_dict)
        print("✅ Signature verified successfully!")
    except razorpay.errors.SignatureVerificationError:
        print("❌ Signature verification failed!")
        
        return redirect('customer_subscriptions')
    
    # Payment is genuine, proceed with activation
    customer_id = request.session.get('customer_id')
    if not customer_id:
        
        return redirect('customer_login')
    
    customer = get_object_or_404(CustomerRegister, id=customer_id)
    
    # Get plan details from session
    plan_type = request.session.get('pending_plan_type', 'basic')
    duration = int(request.session.get('pending_duration', 1))
    amount = int(request.session.get('pending_amount', 0))
    custom_receipt = request.session.get('pending_custom_receipt', '')
    
    # Calculate expiry date
    now = timezone.now()
    expiry = now + timedelta(days=30 * duration)
    
    # Create or update subscription
    CustomerSubscription.objects.update_or_create(
        customer=customer,
        defaults={
            'plan_type': plan_type,
            'duration_months': duration,
            'start_date': now,
            'expiry_date': expiry,
            'is_active': True,
            'razorpay_order_id': order_id,
            'razorpay_payment_id': payment_id,
            'amount_paid': amount,
            'payment_date': now,
            'razorpay_receipt': custom_receipt,
        }
    )
    
    # ✅ SEND EMAIL IN BACKGROUND THREAD (NON-BLOCKING)
    def send_email_in_background():
        """This function runs in a separate thread"""
        try:
            ist = pytz.timezone('Asia/Kolkata')
            now_ist = now.astimezone(ist)
            expiry_ist = expiry.astimezone(ist)
            
            subject = '🎉 Payment Successful - Movieflix Subscription Activated!'
            
            html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f4; font-family: Arial, sans-serif;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td align="center" style="padding: 40px 0;">
                <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <!-- Header with Logo/Brand -->
                    <tr>
                        <td style="padding: 40px 40px 30px 40px; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                            <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: bold;">MOVIEFLIX</h1>
                        </td>
                    </tr>
                    
                    <!-- Main Content -->
                    <tr>
                        <td style="padding: 40px;">
                            <h2 style="margin: 0 0 20px 0; color: #333333; font-size: 24px;">Thanks for subscribing!</h2>
                            
                            <p style="margin: 0 0 20px 0; color: #666666; font-size: 16px; line-height: 1.5;">
                                Hello {customer.customer_first_name} {customer.customer_last_name},
                            </p>
                            
                            <p style="margin: 0 0 30px 0; color: #666666; font-size: 16px; line-height: 1.5;">
                                Your payment has been successfully processed and your subscription is now active. You're all set to enjoy unlimited streaming!
                            </p>
                            
                            <!-- Subscription Details Card -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 30px;">
                                <tr>
                                    <td style="padding: 25px;">
                                        <h3 style="margin: 0 0 15px 0; color: #333333; font-size: 18px;">Your Account Information:</h3>
                                        
                                        <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                            <tr>
                                                <td style="padding: 8px 0; color: #666666; font-size: 14px; width: 40%;">Plan Type</td>
                                                <td style="padding: 8px 0; color: #333333; font-size: 14px; font-weight: bold;">{plan_type.upper()}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0; color: #666666; font-size: 14px;">Duration</td>
                                                <td style="padding: 8px 0; color: #333333; font-size: 14px; font-weight: bold;">{duration} month(s)</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0; color: #666666; font-size: 14px;">Amount Paid</td>
                                                <td style="padding: 8px 0; color: #333333; font-size: 14px; font-weight: bold;">₹{amount // 100}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0; border-top: 1px solid #dee2e6; color: #666666; font-size: 14px;">Start Date</td>
                                                <td style="padding: 8px 0; border-top: 1px solid #dee2e6; color: #333333; font-size: 14px;">{now_ist.strftime('%d %B %Y, %I:%M %p IST')}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0; color: #666666; font-size: 14px;">Expiry Date</td>
                                                <td style="padding: 8px 0; color: #333333; font-size: 14px;">{expiry_ist.strftime('%d %B %Y, %I:%M %p IST')}</td>
                                            </tr>
                                        </table>
                                        
                                        <div style="margin-top: 20px; padding-top: 20px; border-top: 1px solid #dee2e6;">
                                            <p style="margin: 10px 0 5px 0; color: #666666; font-size: 13px;">Receipt ID</p>
                                            <p style="margin: 0; color: #333333; font-size: 13px; font-family: monospace; word-break: break-all;">{custom_receipt}</p>
                                        </div>
                                    </td>
                                </tr>
                            </table>
                            
                            <p style="margin: 0 0 10px 0; color: #666666; font-size: 14px; line-height: 1.5;">
                                Enjoy unlimited streaming of movies and series!
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px 40px; background-color: #f8f9fa; text-align: center;">
                            <p style="margin: 0; color: #999999; font-size: 13px;">
                                Best regards,<br>
                                <strong>MovieFlix Team</strong>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
            
            email_from = settings.EMAIL_HOST_USER
            recipient_list = [customer.customer_email]
            
            send_mail(
                subject,
                '',
                email_from,
                recipient_list,
                fail_silently=True,
                html_message=html_message
            )
            
            print(f"✅ Email sent successfully to {customer.customer_email}")
        except Exception as e:
            print(f"⚠️ Email error: {e}")
    
    # ⭐ START EMAIL THREAD (runs in background, doesn't block)
    email_thread = threading.Thread(target=send_email_in_background)
    email_thread.daemon = True  # Thread will close when main program exits
    email_thread.start()
    
    # Clear session data
    for key in ['pending_plan_type', 'pending_duration', 'pending_amount', 'pending_order_id', 'pending_custom_receipt']:
        if key in request.session:
            del request.session[key]
    
       
    return redirect('customer_subscriptions')





def payment_failed(request):
    """Payment failed or was cancelled"""
    
    return redirect('customer_subscriptions')

def customer_cancel_subscription(request):
    """Cancel active subscription with email confirmation"""
    customer_id = request.session.get('customer_id')
    if not customer_id:
        
        return redirect('customer_login')
    
    customer = get_object_or_404(CustomerRegister, id=customer_id)
    
    # Get active subscription
    current_sub = CustomerSubscription.objects.filter(customer=customer, is_active=True).first()
    
    if not current_sub:
        
        return redirect('customer_subscriptions')
    
    # Store details before cancellation for email
    plan_type = current_sub.plan_type
    expiry_date = current_sub.expiry_date
    
    # Cancel the subscription
    current_sub.is_active = False
    current_sub.save()
    
    # ✅ Send cancellation email with HTML template
    # Convert to IST for display
    ist = pytz.timezone('Asia/Kolkata')
    cancel_time_ist = timezone.now().astimezone(ist)
    expiry_date_ist = expiry_date.astimezone(ist)

    try:
        subject = '❌ Subscription Cancelled - Movieflix'
        
        # HTML Email Template
        html_message = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
</head>
<body style="margin: 0; padding: 0; background-color: #f4f4f4; font-family: Arial, sans-serif;">
    <table role="presentation" style="width: 100%; border-collapse: collapse;">
        <tr>
            <td align="center" style="padding: 40px 0;">
                <table role="presentation" style="width: 600px; border-collapse: collapse; background-color: #ffffff; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
                    <!-- Header with Logo/Brand -->
                    <tr>
                        <td style="padding: 40px 40px 30px 40px; text-align: center; background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);">
                            <h1 style="margin: 0; color: #ffffff; font-size: 32px; font-weight: bold;">MOVIEFLIX</h1>
                        </td>
                    </tr>
                    
                    <!-- Main Content -->
                    <tr>
                        <td style="padding: 40px;">
                            <h2 style="margin: 0 0 20px 0; color: #333333; font-size: 24px;">Subscription Cancelled</h2>
                            
                            <p style="margin: 0 0 20px 0; color: #666666; font-size: 16px; line-height: 1.5;">
                                Hello {customer.customer_first_name} {customer.customer_last_name},
                            </p>
                            
                            <p style="margin: 0 0 30px 0; color: #666666; font-size: 16px; line-height: 1.5;">
                                Your Movieflix subscription has been cancelled as per your request.
                            </p>
                            
                            <!-- Cancellation Details Card -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #fff3cd; border-radius: 8px; margin-bottom: 20px; border-left: 4px solid #ffc107;">
                                <tr>
                                    <td style="padding: 25px;">
                                        <h3 style="margin: 0 0 15px 0; color: #856404; font-size: 18px;">Cancelled Subscription Details:</h3>
                                        
                                        <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                            <tr>
                                                <td style="padding: 8px 0; color: #856404; font-size: 14px; width: 50%;">Plan Type</td>
                                                <td style="padding: 8px 0; color: #333333; font-size: 14px; font-weight: bold;">{plan_type.upper()}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0; color: #856404; font-size: 14px;">Cancellation Date</td>
                                                <td style="padding: 8px 0; color: #333333; font-size: 14px;">{cancel_time_ist.strftime('%d %B %Y, %I:%M %p IST')}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0; color: #856404; font-size: 14px;">Original Expiry Date</td>
                                                <td style="padding: 8px 0; color: #333333; font-size: 14px;">{expiry_date_ist.strftime('%d %B %Y, %I:%M %p IST')}</td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Important Notice -->
                            <div style="background-color: #f8d7da; border-left: 4px solid #dc3545; padding: 15px; margin-bottom: 20px; border-radius: 4px;">
                                <p style="margin: 0 0 5px 0; color: #721c24; font-size: 14px; font-weight: bold;">⚠️ Important Notice</p>
                                <p style="margin: 5px 0 0 0; color: #721c24; font-size: 14px; line-height: 1.5;">
                                    Your subscription has been deactivated immediately. You will no longer have access to premium features.
                                </p>
                            </div>
                            
                            <!-- Come Back Anytime -->
                            <div style="background-color: #d1ecf1; border-left: 4px solid #17a2b8; padding: 15px; margin-bottom: 25px; border-radius: 4px;">
                                <p style="margin: 0 0 5px 0; color: #0c5460; font-size: 14px; font-weight: bold;">💙 Come Back Anytime</p>
                                <p style="margin: 5px 0 0 0; color: #0c5460; font-size: 14px; line-height: 1.5;">
                                    We'd love to have you back! You can resubscribe at any time by visiting our subscriptions page.
                                </p>
                            </div>
                            
                            <p style="margin: 0; color: #666666; font-size: 14px; line-height: 1.5;">
                                If you cancelled by mistake or need assistance, please contact our support team.
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px 40px; background-color: #f8f9fa; text-align: center;">
                            <p style="margin: 0; color: #999999; font-size: 13px;">
                                Best regards,<br>
                                <strong>MovieFlix Team</strong>
                            </p>
                        </td>
                    </tr>
                </table>
            </td>
        </tr>
    </table>
</body>
</html>
"""
        
        email_from = settings.EMAIL_HOST_USER
        recipient_list = [customer.customer_email]
        
        # Send email with HTML content
        send_mail(
            subject, 
            '',  # Plain text version (empty, HTML takes priority)
            email_from, 
            recipient_list, 
            fail_silently=False,
            html_message=html_message  # HTML email content
        )
        print(f"✅ Cancellation email sent to {customer.customer_email}")
        
    except Exception as e:
        print(f"⚠️ Email sending failed: {e}")
    
    
    return redirect('customer_subscriptions')


@customer_session_required
def customer_search_page(request):
    customer_id = request.session.get('customer_id')
    customer = get_object_or_404(CustomerRegister, id=customer_id)
    
    # Fetch the active subscription
    current_sub = CustomerSubscription.objects.filter(customer=customer, is_active=True).first()
    
    # --- NEW: Fetch Random Content for "Explore" Mode ---
    all_movies = list(Movie.objects.all())
    all_series = list(WebSeries.objects.all())

    # Tag them so the template knows which URL to use
    for m in all_movies:
        m.type = 'movie'
    for s in all_series:
        s.type = 'series'

    # Combine and Shuffle
    combined_content = all_movies + all_series
    random.shuffle(combined_content)

    # Take the top 24 items (Random Mix)
    initial_recommendations = combined_content[:24]

    return render(request, 'customer_panel/Internship6-febOS.html', {
        'customer': customer,
        'current_sub': current_sub,
        'initial_recommendations': initial_recommendations, # Pass to template
    })

# // for search page
def live_search_api(request):
    query = request.GET.get('q', '').strip()
    results = []

    if query:
        # 1. Search Movies (Limit to 10 to keep it fast)
        movies = Movie.objects.filter(movie_title__icontains=query)[:10]
        for m in movies:
            results.append({
                'id': m.id,
                'title': m.movie_title,
                'banner': m.movie_banner.url if m.movie_banner else '',
                'director': m.movie_director,
                'type': 'Movie',
                # This URL matches urls.py pattern
                'url': f"/customer_panel/customer_movie_player_page/{m.id}/"
            })

        # 2. Search Web Series
        series = WebSeries.objects.filter(series_title__icontains=query)[:10]
        for s in series:
            results.append({
                'id': s.id,
                'title': s.series_title,
                'banner': s.series_banner.url if s.series_banner else '',
                'director': s.series_director,
                'type': 'Series',
                # This URL matches urls.py pattern
                'url': f"/customer_panel/customer_series_player_page/{s.id}/"
            })

    return JsonResponse({'status': 'success', 'results': results})