from django.db import IntegrityError
from django.shortcuts import render, redirect
from django.shortcuts import get_object_or_404, redirect
from .models import AdminRegister
from django.http import JsonResponse
from django.core.mail import send_mail
from django.conf import settings
from django.contrib import messages
from core.models import Language, Genre, Movie, WebSeries,Season, Episode ,Notification
from datetime import timedelta
from django.utils import timezone
from customer_panel.models import CustomerRegister
from django.urls import reverse
from django.contrib.auth.hashers import make_password, check_password
import random
import string
from customer_panel.models import CustomerSubscription
from django.db.models import Q
from functools import wraps 
from django.views.decorators.csrf import csrf_exempt # Add this

def admin_session_required(view_func):
    @wraps(view_func) # This ensures the original view name is preserved
    def _wrapped_view(request, *args, **kwargs):
        admin_id = request.session.get('admin_id')
        
        # Check if logged in
        if not admin_id:
            return redirect('/admin_panel/admin_login_page/')

        # Check timeout for temporary sessions
        is_persistent = request.session.get('is_persistent', False)
        if not is_persistent:
            last_touch = request.session.get('last_touch')
            # 3600 = 1 hour. Keep it at 5 or 10 for testing
            if last_touch and (timezone.now().timestamp() - last_touch > 5):
                request.session.flush()
                return redirect('/admin_panel/admin_login_page/')
        
        #  Update activity timestamp
        request.session['last_touch'] = timezone.now().timestamp()
        
        return view_func(request, *args, **kwargs)
    return _wrapped_view



# @csrf_exempt # Required for the App version to work without errors
# def admin_register_page(request):
#     if request.method == "POST":
#         fname = request.POST.get('admin_first_name')
#         lname = request.POST.get('admin_last_name')
#         u_email = request.POST.get('admin_email')
#         u_username = request.POST.get('admin_username') 
#         u_mobileno = request.POST.get('admin_mobileno')
#         u_pwd = request.POST.get('admin_password')
#         u_pic = request.FILES.get('admin_profile_pic')

#         try:
#             new_admin = AdminRegister(
#                 admin_first_name=fname,
#                 admin_last_name=lname,
#                 admin_email=u_email,
#                 admin_username=u_username,
#                 admin_mobileno=u_mobileno,
#                 admin_password=make_password(u_pwd),
#                 admin_profile_pic=u_pic
#             )
#             new_admin.save()

#             # --- DUAL MODE LOGIC START ---
#             # If the App is calling this via JavaScript:
#             if request.headers.get('Accept') == 'application/json':
#                 return JsonResponse({'status': 'success', 'message': 'Account created!'})
            
#             # If the Browser is calling this via standard form:
#             return redirect('/admin_panel/admin_login_page/')
#             # --- DUAL MODE LOGIC END ---

#         except IntegrityError:
#             if request.headers.get('Accept') == 'application/json':
#                 return JsonResponse({'status': 'error', 'message': 'Email already exists!'}, status=400)
#             print("Email already exists!")

#     return render(request, 'admin_panel/Internship28-octOR.html')

def admin_register_page(request):
    if request.method == "POST":
        # Using the exact 'admin_' prefix you added to the HTML
         # 1. Capture the data from the HTML 'name' tags
        fname = request.POST.get('admin_first_name')
        lname = request.POST.get('admin_last_name')
        u_email = request.POST.get('admin_email')
        
        # ADD THIS LINE: This grabs what the user typed in the Username box
        u_username = request.POST.get('admin_username') 
        
        u_mobileno = request.POST.get('admin_mobileno')
        u_pwd = request.POST.get('admin_password')
        u_pic = request.FILES.get('admin_profile_pic')

        # 2. Save it to the Database
        new_admin = AdminRegister(
            admin_first_name=fname,
            admin_last_name=lname,
            admin_email=u_email,
            admin_username=u_username, # SAVE THE USERNAME HERE
            admin_mobileno=u_mobileno,
            admin_password=make_password(u_pwd),
            admin_profile_pic=u_pic
        )
        try:
           new_admin.save()
        except IntegrityError:
          # Handle the error, e.g., redirect back with a message
         print("Email already exists!")

        # After saving, send them to the login page
        return redirect('/admin_panel/admin_login_page/')
    
    return render(request, 'admin_panel/Internship28-octOR.html')

# @csrf_exempt  # <--- Essential for the App to bypass CSRF checks
# def admin_login_page(request):
#     # 1. Check if user is already logged in
#     if request.session.get('admin_username'):
#         # If App asks, return JSON success (User already logged in)
#         if request.headers.get('Accept') == 'application/json':
#             return JsonResponse({'status': 'success', 'message': 'Already logged in'})
        
#         return redirect('/admin_panel/admin_dashboard_page/')

#     if request.method == "POST":
#         username_entered = request.POST.get('admin_entered_username')
#         password_entered = request.POST.get('admin_entered_password')
#         keep_signed_in = request.POST.get('keep_signed_in') 
        
#         try:
#             admin = AdminRegister.objects.get(admin_username=username_entered)
            
#             if check_password(password_entered, admin.admin_password):
#                 # --- LOGIN SUCCESS ---
#                 request.session['admin_id'] = admin.id
#                 request.session['admin_username'] = admin.admin_username

#                 if keep_signed_in:
#                     request.session.set_expiry(None)
#                     request.session['is_persistent'] = True
#                 else:
#                     request.session.set_expiry(0)
#                     request.session['is_persistent'] = False
#                     request.session['last_activity'] = timezone.now().timestamp()

#                 # === DUAL MODE START ===
#                 # If the App is calling this via JavaScript:
#                 if request.headers.get('Accept') == 'application/json':
#                     return JsonResponse({'status': 'success', 'message': 'Login successful'})
                
#                 # If the Browser is calling this via standard form:
#                 return redirect('/admin_panel/admin_dashboard_page/')
#                 # === DUAL MODE END ===

#             else:
#                 # --- PASSWORD WRONG ---
#                 if request.headers.get('Accept') == 'application/json':
#                     return JsonResponse({'status': 'error', 'message': 'Invalid Password'}, status=400)
                
#                 return render(request, 'admin_panel/Internship28-octOL.html', {'error': 'Invalid Credentials'})
                
#         except AdminRegister.DoesNotExist:
#             # --- USER NOT FOUND ---
#             if request.headers.get('Accept') == 'application/json':
#                 return JsonResponse({'status': 'error', 'message': 'User does not exist'}, status=400)

#             return render(request, 'admin_panel/Internship28-octOL.html', {'error': 'Invalid Credentials'})
    
#     return render(request, 'admin_panel/Internship28-octOL.html')

def admin_login_page(request):
    # 1. Check if user is already logged in
    if request.session.get('admin_username'):
        return redirect('/admin_panel/admin_dashboard_page/')

    if request.method == "POST":
        username_entered = request.POST.get('admin_entered_username')
        password_entered = request.POST.get('admin_entered_password')
        
        # This gets the 'value' of the checkbox
        keep_signed_in = request.POST.get('keep_signed_in') 
        
        try:
            admin = AdminRegister.objects.get(admin_username=username_entered)
            
            if check_password(password_entered, admin.admin_password):
                request.session['admin_id'] = admin.id
                request.session['admin_username'] = admin.admin_username

                if keep_signed_in:
                    # Checkbox TICKED: Django's 2-week rule (from settings.py)
                    request.session.set_expiry(None)
                    request.session['is_persistent'] = True
                else:
                    # Checkbox UNTICKED: Manual Server-side limit
                    request.session.set_expiry(0)
                    request.session['is_persistent'] = False
                    # Record the exact time they logged in
                    request.session['last_activity'] = timezone.now().timestamp()

                return redirect('/admin_panel/admin_dashboard_page/')
            else:
                return render(request, 'admin_panel/Internship28-octOL.html', {'error': 'Invalid Credentials'})
                
        except AdminRegister.DoesNotExist:
            return render(request, 'admin_panel/Internship28-octOL.html', {'error': 'Invalid Credentials'})
    
    return render(request, 'admin_panel/Internship28-octOL.html')


@csrf_exempt
def admin_logout_action(request):
    # 1. This deletes all session data (username, id, etc.)
    request.session.flush() 
    
    # 2. Check if the request comes from the Mobile App
    if request.headers.get('Accept') == 'application/json':
        return JsonResponse({
            'status': 'success', 
            'message': 'Logged out successfully'
        })

    # 3. Standard Browser Redirect
    return redirect('/admin_panel/admin_login_page/')

@csrf_exempt # Important for the App
def admin_login_forgot_password_action(request):
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            admin = AdminRegister.objects.get(admin_email=email)
            
            # Generate a random temporary password
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            
            # Hash and save it
            admin.admin_password = make_password(temp_password)
            admin.save()
            
            #  PROFESSIONAL HTML EMAIL FOR ADMIN 
            import pytz
            ist = pytz.timezone('Asia/Kolkata')
            now_ist = timezone.now().astimezone(ist)
            
            subject = '🔐 Admin Password Reset - Movieflix'
            
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
                            <p style="margin: 10px 0 0 0; color: #e0e7ff; font-size: 14px; letter-spacing: 2px;">ADMIN PANEL</p>
                        </td>
                    </tr>
                    
                    <!-- Main Content -->
                    <tr>
                        <td style="padding: 40px;">
                            <h2 style="margin: 0 0 20px 0; color: #333333; font-size: 24px;">Admin Password Reset</h2>
                            
                            <p style="margin: 0 0 20px 0; color: #666666; font-size: 16px; line-height: 1.5;">
                                Hello <strong>{admin.admin_first_name} {admin.admin_last_name}</strong>,
                            </p>
                            
                            <p style="margin: 0 0 30px 0; color: #666666; font-size: 16px; line-height: 1.5;">
                                Your admin password has been reset successfully. Below is your temporary password for accessing the admin panel.
                            </p>
                            
                            <!-- Temporary Password Card -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 30px;">
                                <tr>
                                    <td style="padding: 25px;">
                                        <h3 style="margin: 0 0 15px 0; color: #333333; font-size: 18px;">Temporary Admin Password</h3>
                                        
                                        <div style="background-color: #ffffff; padding: 15px; border-radius: 6px; border-left: 4px solid #dc3545; margin-bottom: 15px;">
                                            <p style="margin: 0; font-family: 'Courier New', monospace; font-size: 24px; font-weight: bold; color: #dc3545; letter-spacing: 2px;">
                                                {temp_password}
                                            </p>
                                        </div>
                                        
                                        <div style="background-color: #fff3cd; border-left: 3px solid #ffc107; padding: 12px; border-radius: 4px;">
                                            <p style="margin: 0; color: #856404; font-size: 14px; line-height: 1.5;">
                                                <strong style="color: #e74c3c;">⚠️ Security Alert:</strong><br>
                                                This is a privileged admin account. Please change this password immediately after logging in.
                                            </p>
                                        </div>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Admin Account Details -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 30px;">
                                <tr>
                                    <td style="padding: 25px;">
                                        <h3 style="margin: 0 0 15px 0; color: #333333; font-size: 18px;">Admin Account Details</h3>
                                        
                                        <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                            <tr>
                                                <td style="padding: 8px 0; color: #666666; font-size: 14px; width: 40%;">Email</td>
                                                <td style="padding: 8px 0; color: #333333; font-size: 14px; font-weight: bold;">{admin.admin_email}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0; border-top: 1px solid #dee2e6; color: #666666; font-size: 14px;">Username</td>
                                                <td style="padding: 8px 0; border-top: 1px solid #dee2e6; color: #333333; font-size: 14px; font-weight: bold;">{admin.admin_username}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0; border-top: 1px solid #dee2e6; color: #666666; font-size: 14px;">Reset Time</td>
                                                <td style="padding: 8px 0; border-top: 1px solid #dee2e6; color: #333333; font-size: 14px;">{now_ist.strftime('%d %B %Y, %I:%M %p IST')}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0; border-top: 1px solid #dee2e6; color: #666666; font-size: 14px;">Account Type</td>
                                                <td style="padding: 8px 0; border-top: 1px solid #dee2e6; color: #dc3545; font-size: 14px; font-weight: bold;">Administrator</td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Instructions -->
                            <div style="background-color: #d1ecf1; border-left: 4px solid #17a2b8; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
                                <p style="margin: 0; color: #0c5460; font-size: 14px; line-height: 1.6;">
                                    <strong>Next Steps:</strong><br>
                                    1. Login to the admin panel using the temporary password above<br>
                                    2. Navigate to Admin Profile Settings<br>
                                    3. Change your password immediately to maintain security<br>
                                    4. Use a strong password with letters, numbers, and special characters
                                </p>
                            </div>
                            
                            <p style="margin: 0 0 10px 0; color: #666666; font-size: 14px; line-height: 1.5;">
                                If you did not request this password reset, please contact the system administrator immediately.
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px 40px; background-color: #f8f9fa; text-align: center;">
                            <p style="margin: 0; color: #999999; font-size: 13px;">
                                Best regards,<br>
                                <strong>MovieFlix Admin Team</strong>
                            </p>
                            <p style="margin: 10px 0 0 0; color: #cccccc; font-size: 11px;">
                                This is an automated admin notification. Do not share this password.
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
            
        
        # === DUAL MODE RESPONSE ===
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({'status': 'success', 'message': f'Temporary password sent to {email}'})

            messages.success(request, f"✅ A temporary password has been sent to {email}.")
            return redirect('admin_login')
            
        except AdminRegister.DoesNotExist:
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({'status': 'error', 'message': 'Email not registered'}, status=400)
            
            messages.error(request, "Error: That email address is not registered.")
            return redirect('admin_login')

        except Exception as e:
            if request.headers.get('Accept') == 'application/json':
                return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
            
            messages.error(request, f"Mail delivery failed: {e}")
            return redirect('admin_login')
    
    return redirect('admin_login')


@admin_session_required
def admin_dashboard_page(request):
    # The decorator has already checked the session and updated last_touch!
    admin_id = request.session.get('admin_id')
    admin = AdminRegister.objects.get(id=admin_id)

    movie_count = Movie.objects.count()
    language_count = Language.objects.count()
    genre_count = Genre.objects.count()
    series_count = WebSeries.objects.count()

    context = {
        'admin': admin,
        'movie_count': movie_count,
        'language_count': language_count,
        'genre_count': genre_count,
        'series_count': series_count,
    }
    return render(request, 'admin_panel/Internship4-octOD.html', context)

def admin_update_profile(request):
    if request.method == "POST":
        admin_id = request.session.get('admin_id')
        admin = AdminRegister.objects.get(id=admin_id)

        # Update text fields
        admin.admin_first_name = request.POST.get('admin_modal_first_name')
        admin.admin_last_name = request.POST.get('admin_modal_last_name')
        admin.admin_email = request.POST.get('admin_modal_email')
        admin.admin_mobileno = request.POST.get('admin_modal_mobileno')
        
        # SAVE THE USERNAME 
        admin.admin_username = request.POST.get('admin_modal_username')

        # SAFELY UPDATE PROFILE PIC
        new_pic = request.FILES.get('admin_profile_pic')
        if new_pic: # Only updates if you actually chose a new file
            admin.admin_profile_pic = new_pic

        admin.save()
        # DYNAMIC REDIRECT: 
        # HTTP_REFERER is the URL the user came from.
        # We use 'customer_profile_settings' as a backup just in case referer is missing.
        return redirect(request.META.get('HTTP_REFERER', '/admin_panel/admin_dashboard_page/'))
       

# --
@admin_session_required
def admin_language_page(request):

    admin_id = request.session.get('admin_id')
    admin = AdminRegister.objects.get(id=admin_id)
    # Fetch all languages from the database
    languages = Language.objects.all()
    
    # Get error message from session if it exists
    error_message = request.session.pop('language_error', None)
    
    return render(request, "admin_panel/Internship4-octOLang.html", {
        'admin': admin,
        'languages': languages,
        'error_message': error_message  # ADD THIS LINE
    })


def add_language(request):
    if request.method == "POST":
        lang_name = request.POST.get('admin_language_name')
        if lang_name:
            # Check if this language already exists
            if Language.objects.filter(language_name=lang_name).exists():
                request.session['language_error'] = f"'{lang_name}' already exists!"
            else:
                Language.objects.create(language_name=lang_name)
    return redirect('/admin_panel/admin_language_page/')


def delete_language(request, lang_id):  # ← CHANGED: language_id to lang_id
    Language.objects.get(id=lang_id).delete()
    return redirect('/admin_panel/admin_language_page/')


def update_language(request, lang_id):  # ← CHANGED: language_id to lang_id
    if request.method == "POST":
        language = get_object_or_404(Language, id=lang_id)  # ← CHANGED: lang_id here too
        
        new_language_name = request.POST.get('language_name')
        
        # Check if the updated language name already exists (excluding current language)
        if Language.objects.filter(language_name=new_language_name).exclude(id=lang_id).exists():
            request.session['language_error'] = f"'{new_language_name}' already exists!"
        else:
            language.language_name = new_language_name
            language.save()
        
        return redirect('/admin_panel/admin_language_page/')


@admin_session_required
def admin_genre_page(request):
    admin_id = request.session.get('admin_id')
    admin = AdminRegister.objects.get(id=admin_id)
    # Fetch all genres from the database
    genres = Genre.objects.all()
    
    # Get error message from session if it exists
    error_message = request.session.pop('genre_error', None)
    
    return render(request, "admin_panel/Internship4-octOGenre.html", {
        'admin': admin,
        'genres': genres,
        'error_message': error_message  # ADD THIS LINE
    })


def add_genre(request):
    if request.method == "POST":
        cat = request.POST.get('admin_category')
        gen = request.POST.get('admin_genre_name')
        if cat and gen:
            # Check if this combination already exists
            if Genre.objects.filter(category_name=cat, genre_name=gen).exists():
                # Store error message in session
                request.session['genre_error'] = f"'{gen}' already exists in {cat} category!"
            else:
                # Only create if it doesn't exist
                Genre.objects.create(category_name=cat, genre_name=gen)
    return redirect('/admin_panel/admin_genre_page/')


def delete_genre(request, genre_id):
    Genre.objects.get(id=genre_id).delete()
    return redirect('/admin_panel/admin_genre_page/')


def update_genre(request, genre_id):
    if request.method == "POST":
        genre = get_object_or_404(Genre, id=genre_id)
        
        new_category = request.POST.get('category_name')
        new_genre_name = request.POST.get('genre_name')
        
        # Check if the updated combination already exists (excluding current genre)
        if Genre.objects.filter(category_name=new_category, genre_name=new_genre_name).exclude(id=genre_id).exists():
            request.session['genre_error'] = f"'{new_genre_name}' already exists in {new_category} category!"
        else:
            # Update only if no duplicate
            genre.category_name = new_category
            genre.genre_name = new_genre_name
            genre.save()
        
        return redirect('admin_genre_page')

@admin_session_required
def admin_movie_page(request):
    # ---  LOGIC TO FETCH ADMIN DATA ---
    admin_id = request.session.get('admin_id')
    admin_data = None
    if admin_id:
        admin_data = AdminRegister.objects.get(id=admin_id)
    else:
        return redirect('admin_login') # Security: send back to login if no session

    # --- EXISTING FILTER LOGIC ---
    selected_lang = request.GET.get('lang')
    selected_genre = request.GET.get('genre')
    movies = Movie.objects.all().order_by('-id')

    if selected_lang:
        movies = movies.filter(movie_language_id=selected_lang)
    if selected_genre:
        movies = movies.filter(movie_genre_id=selected_genre)

    languages = Language.objects.all()
    genres = Genre.objects.filter(category_name='Movie')
    
    # --- UPDATE THE CONTEXT TO INCLUDE 'admin' ---
    return render(request, 'admin_panel/Internship11-decOM.html', {
        'movies': movies,
        'languages': languages,
        'genres': genres,
        'admin': admin_data  # Pass the admin object here
    })




def add_movie_action(request):
    if request.method == "POST":
        lang_id = request.POST.get('movie_language')
        gen_id = request.POST.get('movie_genre')
        movie_name = request.POST.get('movie_title')
        movie_banner = request.FILES.get('movie_banner')

        new_movie = Movie(
            movie_title=movie_name,
            movie_director=request.POST.get('movie_director'),
            movie_release_date=request.POST.get('movie_release_date'),
            movie_language_id=lang_id,
            movie_genre_id=gen_id,
            movie_banner=request.FILES.get('movie_banner'),
            movie_duration=request.POST.get('movie_duration'),
            movie_description=request.POST.get('movie_description'),
            movie_video_url=request.POST.get('movie_video_url')
        )
        new_movie.save()

        # --- STEP 1: GENERATE THE REDIRECT URL ---
        # This creates the link /customer/movie_player/5/ (example)
        # Verify that 'customer_movie_player' is the 'name' in your urls.py
        movie_player_url = reverse('customer_movie_player_page', args=[new_movie.id]) + "?play=true"


 # --- UPDATED NOTIFICATION LOGIC WITH ROLES ---
        notifications_list = []

        # 1. FETCH ONLY PREMIUM CUSTOMERS
        # We filter CustomerRegister by checking if they have an active 'premium' subscription
        premium_customers = CustomerRegister.objects.filter(
            customersubscription__plan_type='premium',
            customersubscription__is_active=True,
            customersubscription__expiry_date__gt=timezone.now()
        ).values_list('customer_username', flat=True)

        for username in premium_customers:
            notifications_list.append(
                Notification(
                    recipient_username=username,
                    user_role='customer',
                    title="New Movie Added! (Premium Exclusive)",
                    message=f"'{movie_name}' is now available on Movieflix.",
                    redirect_url=movie_player_url,
                    image=movie_banner,
                )
            )

    
        # 2. Fetch Admin Usernames and assign 'admin' role
        admin_usernames = AdminRegister.objects.values_list('admin_username', flat=True)
        for username in admin_usernames:
            notifications_list.append(
                Notification(
                    recipient_username=username,
                    user_role='admin',  # Add this field
                    title="New Movie Added!",
                    message=f"'{movie_name}' has been added to the system.",
                    redirect_url=movie_player_url,
                    image=movie_banner
                )
            )
        
        # 3. Save all unique notifications
        Notification.objects.bulk_create(notifications_list)
        
        return redirect('admin_movie_page')

    movies = Movie.objects.all()
    languages = Language.objects.all()
    genres = Genre.objects.all()
    
    return render(request, 'Internship11-decOM.html', {
        'movies': movies,
        'languages': languages,
        'genres': genres
    })




def delete_movie(request, movie_id):
    # Fetch the movie or return a 404 error if it doesn't exist
    movie = get_object_or_404(Movie, id=movie_id)
    movie.delete()
    return redirect('admin_movie_page')


def update_movie(request, movie_id):
    if request.method == "POST":
        movie = get_object_or_404(Movie, id=movie_id)
        
        # Updating all requested fields
        movie.movie_title = request.POST.get('movie_title')
        movie.movie_director = request.POST.get('movie_director')
        movie.movie_release_date = request.POST.get('movie_release_date')
        movie.movie_duration = request.POST.get('movie_duration')
        movie.movie_description = request.POST.get('movie_description')
        movie.movie_video_url = request.POST.get('movie_video_url')
        
        # Updating Foreign Keys for Language and Genre
        movie.movie_language_id = request.POST.get('movie_language')
        movie.movie_genre_id = request.POST.get('movie_genre')
        
        # Update banner only if a new file is uploaded
        if request.FILES.get('movie_banner'):
            movie.movie_banner = request.FILES.get('movie_banner')
            
        movie.save()
        return redirect('admin_movie_page')

# --

@admin_session_required
def admin_web_series_page(request):
    admin_id = request.session.get('admin_id')
    admin_data = AdminRegister.objects.get(id=admin_id)
    
    #  Get the filter values from the URL
    lang_id = request.GET.get('language')
    genre_id = request.GET.get('genre')

    #  Start with all webseries
    all_webseries = WebSeries.objects.all().order_by('-created_at')

    #  Apply filters using the CORRECT field names from your error message
    if lang_id:
        # Changed from web_series_language_id to series_language_id
        all_webseries = all_webseries.filter(series_language_id=lang_id)
    
    if genre_id:
        # Changed from web_series_genre_id to series_genre_id
        all_webseries = all_webseries.filter(series_genre_id=genre_id)

    #  Fetch languages and genres for dropdowns
    languages = Language.objects.all()
    genres = Genre.objects.filter(category_name='Web Series')
    
    return render(request, 'admin_panel/Internship23-decOW.html', {
        'all_webseries': all_webseries,
        'admin': admin_data,
        'languages': languages,
        'genres': genres,
        'selected_lang': lang_id,
        'selected_gen': genre_id
    })


def add_web_series_action(request):
    if request.method == "POST":
        series_title = request.POST.get('series_title')
        series_banner=request.FILES.get('series_banner')
        
        new_series = WebSeries.objects.create(
            series_title=series_title,
            series_director=request.POST.get('series_director'),
            series_language_id=request.POST.get('series_language'),
            series_genre_id=request.POST.get('series_genre'),
            total_seasons=request.POST.get('total_seasons'),
            release_date=request.POST.get('release_date'), 
            series_banner=request.FILES.get('series_banner')
        )
        new_series.save()

        series_player_url = reverse('customer_series_player_page', args=[new_series.id])
        

        notifications_list = []
        
        # 1. FETCH ONLY PREMIUM CUSTOMERS
        # We filter CustomerRegister by checking if they have an active 'premium' subscription
        premium_customers = CustomerRegister.objects.filter(
            customersubscription__plan_type='premium',
            customersubscription__is_active=True,
            customersubscription__expiry_date__gt=timezone.now()
        ).values_list('customer_username', flat=True)

        for username in premium_customers:
            notifications_list.append(
                Notification(
                    recipient_username=username,
                    user_role='customer',
                    title="New Web Series! (Premium Exclusive)", message=f"'{series_title}' is now available on Movieflix!",
                    redirect_url=series_player_url,
                    image=series_banner
                    ),
                    
            )

        # 2. Add for Admins
        admin_usernames = AdminRegister.objects.values_list('admin_username', flat=True)
        for uname in admin_usernames:
            notifications_list.append(
                Notification(recipient_username=uname,
                              user_role='admin', 
                             title="New Web Series!", message=f"'{series_title}' added to system.",
                             redirect_url=series_player_url,
                             image=series_banner
                            )
            )
                             
        
        Notification.objects.bulk_create(notifications_list)
        return redirect(f'/admin_panel/admin_web_series_page/?open_modal={new_series.id}')
    
    

def delete_web_series_action(request):
    if request.method == "POST":
        series_id = request.POST.get('series_id')
        
        # This will delete the Series, and CASCADE will handle Seasons & Episodes
        series = get_object_or_404(WebSeries, id=series_id)
        series_name = series.series_title
        series.delete()
        
        
    return redirect('/admin_panel/admin_web_series_page/')


def add_season_action(request):
    if request.method == "POST":
        series_id = request.POST.get('series_id')
        series = get_object_or_404(WebSeries, id=series_id)
        
        last_season = series.seasons_list.all().order_by('season_order').last()
        next_order = (last_season.season_order + 1) if last_season else 1

        # We use a unique placeholder name to identify it later
        Season.objects.create(
            series=series,
            season_name="Untitled Season", 
            season_order=next_order
        )
        
        series.total_seasons = series.seasons_list.count()
        series.save()

        return redirect(f'/admin_panel/admin_web_series_page/?open_season_modal={series_id}')

# views.py

def define_seasons_action(request):
    if request.method == "POST":
        series_id = request.POST.get('series_id')
        # Add the order list here
        new_names = request.POST.getlist('season_names[]')
        season_orders = request.POST.getlist('season_orders[]') # NEW: Capture the order
        release_dates = request.POST.getlist('season_release_dates[]')
        descriptions = request.POST.getlist('season_descriptions[]')
        
        series = WebSeries.objects.get(id=series_id)
        # Fetch current seasons ordered by current order
        current_seasons = series.seasons_list.all().order_by('season_order')
        notifications_list = []

        for index, name in enumerate(new_names):
            if not name: continue
            
            # Use the order from the form, or fall back to index+1
            order = season_orders[index] if index < len(season_orders) else (index + 1)
            rel_date = release_dates[index] if index < len(release_dates) else None
            s_desc = descriptions[index] if index < len(descriptions) else ""
            banner = request.FILES.get(f'season_banner_{index}')

            send_alert = False

            if index < len(current_seasons):
                # Updating Existing Season
                season = current_seasons[index]
                if season.season_name == "Untitled Season" and name != "Untitled Season":
                    send_alert = True

                season.season_name = name
                season.season_order = order  # NEW: Update the order
                season.season_description = s_desc 
                if rel_date: season.season_release_date = rel_date
                if banner: season.season_banner = banner
                season.save()
            else:
                # Creating New Season
                season = Season.objects.create(
                    series=series,
                    season_name=name,
                    season_order=order, # NEW: Use the provided order
                    season_release_date=rel_date,
                    season_banner=banner,
                    season_description=s_desc
                )
                send_alert = True

            series_player_url = reverse('customer_series_player_page', args=[series_id]) + f"?season_id={season.id}"

            if send_alert:
                # Add image=season.season_banner so the notification shows the image
                premium_customers = CustomerRegister.objects.filter(
                    customersubscription__plan_type='premium',
                    customersubscription__is_active=True,
                    customersubscription__expiry_date__gt=timezone.now()
                ).values_list('customer_username', flat=True)
                
                admin_usernames = AdminRegister.objects.values_list('admin_username', flat=True)

                for username in premium_customers:
                    notifications_list.append(
                        Notification(
                            recipient_username=username,
                            user_role='customer',
                            title="New Season Alert! (Premium Exclusive)",
                            message=f"'{name}' of '{series.series_title}' is now available!",
                            redirect_url=series_player_url,
                            image=season.season_banner # ADDED THIS
                        )
                    )
                for username in admin_usernames:
                    notifications_list.append(
                        Notification(
                            recipient_username=username,
                            user_role='admin',
                            title="System Update: New Season",
                            message=f"Season '{name}' was added to {series.series_title}.",
                            redirect_url=series_player_url,
                            image=season.season_banner # ADDED THIS
                        )
                    )

        if notifications_list:
            Notification.objects.bulk_create(notifications_list)

        return redirect(f'/admin_panel/admin_web_series_page/?open_episode_modal={series_id}')


def add_episode_action(request):
    if request.method == "POST":
        # 1. Capture data from POST
        series_id = request.POST.get('series_id')
        season_id = request.POST.get('season_id')
        ep_title = request.POST.get('ep_title')
        ep_url = request.POST.get('ep_url')
        ep_release_date = request.POST.get('ep_release_date')
        duration = request.POST.get('episode_duration')
        description = request.POST.get('episode_description')
        ep_banner = request.FILES.get('ep_banner')
        ep_num = request.POST.get('episode_number')

        # 2. Create the Episode object
        new_episode = Episode.objects.create(
            series_id=series_id,
            season_id=season_id,
            episode_title=ep_title,
            video_url=ep_url,
            episode_release_date=ep_release_date,
            episode_duration=duration,
            episode_description=description,
            episode_banner=ep_banner,
            episode_number = ep_num
            
        )
        new_episode.save()

        # 3. Get the Series name for the notification message
        season_obj = get_object_or_404(Season, id=season_id)
        series_name = season_obj.series.series_title

        series_player_url = reverse('customer_series_player_page', args=[series_id]) + f"?season_id={season_id}&episode_id={new_episode.id}"

        # 4. Prepare notification list following your established pattern
        notifications_list = []

        # Fetch Customer Usernames for customers with notifications enabled

                # 1. FETCH ONLY PREMIUM CUSTOMERS
        # We filter CustomerRegister by checking if they have an active 'premium' subscription
        premium_customers = CustomerRegister.objects.filter(
            customersubscription__plan_type='premium',
            customersubscription__is_active=True,
            customersubscription__expiry_date__gt=timezone.now()
        ).values_list('customer_username', flat=True)

        for username in premium_customers:
            notifications_list.append(
                Notification(
                    recipient_username=username,
                    user_role='customer',
                    title="New Episode Alert! (Premium Exclusive)",
                    message=f"'{ep_title}' has been added to {series_name}.",
                    redirect_url=series_player_url,
                    image=ep_banner
                )
            )

        # Fetch Admin Usernames for admins with notifications enabled
        admin_usernames = AdminRegister.objects.values_list('admin_username', flat=True)
        
        for username in admin_usernames:
            notifications_list.append(
                Notification(
                    recipient_username=username,
                    user_role='admin',
                    title="System Update: New Episode",
                    message=f"Episode '{ep_title}' was successfully added to {series_name}.",
                    redirect_url=series_player_url,
                    image=ep_banner
                )
            )

        # 5. Save all notifications at once
        if notifications_list:
            Notification.objects.bulk_create(notifications_list)

        return redirect('/admin_panel/admin_web_series_page/')



def update_series_basic_action(request):
    if request.method == "POST":
        series_id = request.POST.get('series_id')
        series = get_object_or_404(WebSeries, id=series_id)
        
        # Update Text Fields
        series.series_title = request.POST.get('series_title')
        series.series_director = request.POST.get('series_director')
        
        # Update Foreign Keys (Language & Genre)
        series.series_language_id = request.POST.get('series_language')
        series.series_genre_id = request.POST.get('series_genre')
        
        # Update Banner if provided
        new_banner = request.FILES.get('series_banner')
        if new_banner:
            series.series_banner = new_banner
            
        series.save()
        
        
    return redirect('/admin_panel/admin_web_series_page/') 


# // used for delete episode action
def update_episode_action(request):
    if request.method == "POST":
        ep_id = request.POST.get('ep_id')
        try:
            episode = Episode.objects.get(id=ep_id)
            
            # Use the 'name' attributes from your JavaScript: ep_name, ep_url, ep_date
            episode.episode_title = request.POST.get('ep_name')
            episode.video_url = request.POST.get('ep_url')
            
            # Update Date
            new_date = request.POST.get('ep_date')
            if new_date:
                episode.episode_release_date = new_date
            
            # Update Banner File
            if request.FILES.get('ep_banner'):
                episode.episode_banner = request.FILES.get('ep_banner')
                
            episode.save()
            
        except Episode.DoesNotExist:
            messages.error(request,)
            
    return redirect('/admin_panel/admin_web_series_page/')






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
            'url': ep.video_url, # Check if your model field is video_url or episode_video_url
            'release_date': ep.episode_release_date.strftime('%Y-%m-%d') if ep.episode_release_date else '',
            'duration': ep.episode_duration, # ADD THIS
            'description': ep.episode_description, # ADD THIS

            'episode_number':ep.episode_number ,
            
            # 1. Current Episode Banner
            'episode_banner_url': ep.episode_banner.url if ep.episode_banner else None,
            
            # 2. Add Season Banner (accessed via the relationship)
            'season_banner_url': ep.season.season_banner.url if ep.season and ep.season.season_banner else None 
        })
        
    return JsonResponse({'episodes': episode_list})

# views.py

def update_bulk_episodes_action(request):
    if request.method == "POST":
        # 1. Use .getlist() to capture all arrays from the form
        ep_ids = request.POST.getlist('ep_id[]')
        titles = request.POST.getlist('ep_title[]')
        urls = request.POST.getlist('ep_url[]')
        dates = request.POST.getlist('ep_release_date[]')
        durations = request.POST.getlist('ep_duration[]')
        descriptions = request.POST.getlist('ep_description[]')
        ep_numbers = request.POST.getlist('ep_number[]')

        # 2. Iterate through the IDs to update each episode record
        for i in range(len(ep_ids)):
            try:
                episode = Episode.objects.get(id=ep_ids[i])
                episode.episode_title = titles[i]
                episode.video_url = urls[i]
                episode.episode_duration = durations[i]
                episode.episode_description = descriptions[i]
                episode.episode_number = int(ep_numbers[i])
                
                # Check if a date was actually selected
                if i < len(dates) and dates[i]:
                    episode.episode_release_date = dates[i]

                # 3. Match the specific banner file to this episode index
                # Matches your JS: <input type="file" name="ep_banner_${index}">
                banner_field_name = f'ep_banner_{i}'
                if banner_field_name in request.FILES:
                    episode.episode_banner = request.FILES[banner_field_name]

                episode.save()
            except Episode.DoesNotExist:
                continue

        
    
    return redirect('/admin_panel/admin_web_series_page/')


def delete_episode_action(request):
    if request.method == "POST":
        ep_id = request.POST.get('ep_id')
        Episode.objects.filter(id=ep_id).delete()
        
    return redirect('/admin_panel/admin_web_series_page/')


def delete_season_action(request):
    if request.method == "POST":
        season_id = request.POST.get('season_id')
        
        if not season_id:
            
            return redirect(request.META.get('HTTP_REFERER', '/admin_panel/'))

        # Fetch the season object
        season = get_object_or_404(Season, id=season_id)
        
        # CHANGE: Changed 'web_series' to 'series' to match your model
        series = season.series 
        series_id = series.id 
        
        # Delete the season record
        season.delete()
        
        # Update the total_seasons field on the series
        # Using the related_name 'seasons_list' as seen in your other functions
        series.total_seasons = series.seasons_list.count()
        series.save()
        
        
        
        return redirect(f'/admin_panel/admin_web_series_page/?open_season_modal={series_id}')
    
    return redirect('/admin_panel/admin_web_series_page/')

@admin_session_required
def admin_profile_settings_page(request):

    admin_id = request.session.get('admin_id')
    admin = AdminRegister.objects.get(id=admin_id)
    return render(request, 'admin_panel/Internship5-decOP.html', {
        'admin': admin  # Pass the admin object here
    })

def verify_old_password(request):
    """AJAX endpoint to verify old password"""
    if request.method == "POST":
        admin_id = request.session.get('admin_id')
        old_password = request.POST.get('old_password')
        
        try:
            admin = AdminRegister.objects.get(id=admin_id)
            # Use check_password to verify against hashed version
            if check_password(old_password, admin.admin_password):
                return JsonResponse({'status': 'success'})
            else:
                return JsonResponse({'status': 'failed', 'message': 'Incorrect password'})
        except AdminRegister.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Admin not found'})
    
    return JsonResponse({'status': 'error', 'message': 'Invalid request'})

def admin_change_password_action(request):
    if request.method == "POST":
        admin_id = request.session.get('admin_id')
        old_pwd = request.POST.get('old_password')
        new_pwd = request.POST.get('new_password')
        confirm_pwd = request.POST.get('confirm_new_password')
        
        admin = get_object_or_404(AdminRegister, id=admin_id)
        
        # Verify old password with check_password
        if check_password(old_pwd, admin.admin_password):
            if new_pwd == confirm_pwd:
                admin.admin_password = make_password(new_pwd)  # Hash new password
                admin.save()
                messages.success(request, "Password updated successfully!")
            else:
                messages.error(request, "New passwords did not match.")
        else:
            messages.error(request, "Incorrect old password.")
    
    return redirect('admin_profile_settings')

def admin_forgot_password_action(request):
    """Same logic but redirects to profile settings instead of login"""
    if request.method == "POST":
        email = request.POST.get('email')
        try:
            admin = AdminRegister.objects.get(admin_email=email)
            
            # Generate a random temporary password
            temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=10))
            
            # Hash and save it
            admin.admin_password = make_password(temp_password)
            admin.save()
            
            # ⭐ PROFESSIONAL HTML EMAIL FOR ADMIN ⭐
            import pytz
            ist = pytz.timezone('Asia/Kolkata')
            now_ist = timezone.now().astimezone(ist)
            
            subject = '🔐 Admin Password Reset - Movieflix'
            
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
                            <p style="margin: 10px 0 0 0; color: #e0e7ff; font-size: 14px; letter-spacing: 2px;">ADMIN PANEL</p>
                        </td>
                    </tr>
                    
                    <!-- Main Content -->
                    <tr>
                        <td style="padding: 40px;">
                            <h2 style="margin: 0 0 20px 0; color: #333333; font-size: 24px;">Admin Password Reset</h2>
                            
                            <p style="margin: 0 0 20px 0; color: #666666; font-size: 16px; line-height: 1.5;">
                                Hello <strong>{admin.admin_first_name} {admin.admin_last_name}</strong>,
                            </p>
                            
                            <p style="margin: 0 0 30px 0; color: #666666; font-size: 16px; line-height: 1.5;">
                                Your admin password has been reset successfully. Below is your temporary password for accessing the admin panel.
                            </p>
                            
                            <!-- Temporary Password Card -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 30px;">
                                <tr>
                                    <td style="padding: 25px;">
                                        <h3 style="margin: 0 0 15px 0; color: #333333; font-size: 18px;">Temporary Admin Password</h3>
                                        
                                        <div style="background-color: #ffffff; padding: 15px; border-radius: 6px; border-left: 4px solid #dc3545; margin-bottom: 15px;">
                                            <p style="margin: 0; font-family: 'Courier New', monospace; font-size: 24px; font-weight: bold; color: #dc3545; letter-spacing: 2px;">
                                                {temp_password}
                                            </p>
                                        </div>
                                        
                                        <div style="background-color: #fff3cd; border-left: 3px solid #ffc107; padding: 12px; border-radius: 4px;">
                                            <p style="margin: 0; color: #856404; font-size: 14px; line-height: 1.5;">
                                                <strong style="color: #e74c3c;">⚠️ Security Alert:</strong><br>
                                                This is a privileged admin account. Please change this password immediately after logging in.
                                            </p>
                                        </div>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Admin Account Details -->
                            <table role="presentation" style="width: 100%; border-collapse: collapse; background-color: #f8f9fa; border-radius: 8px; margin-bottom: 30px;">
                                <tr>
                                    <td style="padding: 25px;">
                                        <h3 style="margin: 0 0 15px 0; color: #333333; font-size: 18px;">Admin Account Details</h3>
                                        
                                        <table role="presentation" style="width: 100%; border-collapse: collapse;">
                                            <tr>
                                                <td style="padding: 8px 0; color: #666666; font-size: 14px; width: 40%;">Email</td>
                                                <td style="padding: 8px 0; color: #333333; font-size: 14px; font-weight: bold;">{admin.admin_email}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0; border-top: 1px solid #dee2e6; color: #666666; font-size: 14px;">Username</td>
                                                <td style="padding: 8px 0; border-top: 1px solid #dee2e6; color: #333333; font-size: 14px; font-weight: bold;">{admin.admin_username}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0; border-top: 1px solid #dee2e6; color: #666666; font-size: 14px;">Reset Time</td>
                                                <td style="padding: 8px 0; border-top: 1px solid #dee2e6; color: #333333; font-size: 14px;">{now_ist.strftime('%d %B %Y, %I:%M %p IST')}</td>
                                            </tr>
                                            <tr>
                                                <td style="padding: 8px 0; border-top: 1px solid #dee2e6; color: #666666; font-size: 14px;">Account Type</td>
                                                <td style="padding: 8px 0; border-top: 1px solid #dee2e6; color: #dc3545; font-size: 14px; font-weight: bold;">Administrator</td>
                                            </tr>
                                        </table>
                                    </td>
                                </tr>
                            </table>
                            
                            <!-- Instructions -->
                            <div style="background-color: #d1ecf1; border-left: 4px solid #17a2b8; padding: 15px; border-radius: 4px; margin-bottom: 20px;">
                                <p style="margin: 0; color: #0c5460; font-size: 14px; line-height: 1.6;">
                                    <strong>Next Steps:</strong><br>
                                    1. Login to the admin panel using the temporary password above<br>
                                    2. Navigate to Admin Profile Settings<br>
                                    3. Change your password immediately to maintain security<br>
                                    4. Use a strong password with letters, numbers, and special characters
                                </p>
                            </div>
                            
                            <p style="margin: 0 0 10px 0; color: #666666; font-size: 14px; line-height: 1.5;">
                                If you did not request this password reset, please contact the system administrator immediately.
                            </p>
                        </td>
                    </tr>
                    
                    <!-- Footer -->
                    <tr>
                        <td style="padding: 30px 40px; background-color: #f8f9fa; text-align: center;">
                            <p style="margin: 0; color: #999999; font-size: 13px;">
                                Best regards,<br>
                                <strong>MovieFlix Admin Team</strong>
                            </p>
                            <p style="margin: 10px 0 0 0; color: #cccccc; font-size: 11px;">
                                This is an automated admin notification. Do not share this password.
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
            
        except AdminRegister.DoesNotExist:
            messages.error(request, "Error: That email address is not registered as an admin.")
        except Exception as e:
            messages.error(request, f"Mail delivery failed: {e}")
    
    return redirect('admin_profile_settings')




# Add this new view function
@admin_session_required
def admin_subscriptions_page(request):
    admin_id = request.session.get('admin_id')
    admin = AdminRegister.objects.get(id=admin_id)
    
    # Get filter parameters from URL
    plan_filter = request.GET.get('plan', '')
    status_filter = request.GET.get('status', '')
    search_query = request.GET.get('search', '')
    
    
    # Start with all subscriptions
    subscriptions = CustomerSubscription.objects.select_related('customer').all().order_by('-start_date')
    
    # Apply filters
    if plan_filter:
        subscriptions = subscriptions.filter(plan_type=plan_filter)
    
    if status_filter == 'active':
        subscriptions = subscriptions.filter(is_active=True, expiry_date__gt=timezone.now())
    elif status_filter == 'expired':
        subscriptions = subscriptions.filter(Q(is_active=False) | Q(expiry_date__lte=timezone.now()))
    
    if search_query:
        subscriptions = subscriptions.filter(
            Q(customer__customer_username__icontains=search_query) |
            Q(customer__customer_email__icontains=search_query) |
            Q(razorpay_receipt__icontains=search_query)
        )
    
    # Count statistics
    total_subscriptions = CustomerSubscription.objects.count()
    active_subscriptions = CustomerSubscription.objects.filter(
        is_active=True, 
        expiry_date__gt=timezone.now()
    ).count()
    premium_count = CustomerSubscription.objects.filter(plan_type='premium').count()
    basic_count = CustomerSubscription.objects.filter(plan_type='basic').count()
    
    context = {
        'admin': admin,
        'subscriptions': subscriptions,
        'total_subscriptions': total_subscriptions,
        'active_subscriptions': active_subscriptions,
        'premium_count': premium_count,
        'basic_count': basic_count,
        'selected_plan': plan_filter,
        'selected_status': status_filter,
        'search_query': search_query,
        'now': timezone.now(),
        
    }
    
    return render(request, 'admin_panel/Internship19-janOS.html', context)


# Add this delete subscription action
def delete_subscription_action(request):
    if request.method == 'POST':
        sub_id = request.POST.get('sub_id')
        try:
            subscription = CustomerSubscription.objects.get(id=sub_id)
            customer_name = subscription.customer.customer_username
            subscription.delete()
           
        except CustomerSubscription.DoesNotExist:
            messages.error(request,)
        
        return redirect('admin_subscriptions_page')
