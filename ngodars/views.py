from django.shortcuts import render, redirect
from django.contrib import messages
from datetime import datetime
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q
from django.utils import timezone
from ngodars.models import USER, MERCHANT, ADDRESS, PREMISE, ITEM, BOOKING
from django.contrib.auth.hashers import make_password, check_password

# Create your views here.

#home section
def index(request):
    return render(request, 'home/index.html')

def login(request):
    if request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')

        # Find the user with the given email
        try:
            user = USER.objects.get(email=email)
        except USER.DoesNotExist:
            user = None

        if user:
            # Check the hashed password
            if check_password(password, user.password):
                request.session['user_type'] = 'user'  # Adjust based on your user type logic
                request.session['user_id'] = user.userID
                return redirect('user_home')
            else:
                messages.error(request, "Password is incorrect.")
        else:
            messages.error(request, "Email not found. Please sign up first.")
    return render(request, 'home/login.html')

def search(model, email):
    try:
        return model.objects.get(email=email)
    except model.DoesNotExist:
        return None

def signup(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')

        # Check if passwords match
        if password != confirm_password:
            messages.error(request, 'Passwords do not match. Please try again.')
            return render(request, 'home/signup.html')

        # Check if the email already exists
        if USER.objects.filter(email=email).exists():
            messages.error(request, 'The email has been taken. Please try again.')
            return render(request, 'home/signup.html')

        # Save the user
        try:
            user = USER(
                username=username,
                email=email,
                phone = phone,
                password=make_password(password)  # Hash the password
            )
            user.save()

            # Save phone number in a related model (if needed, as User model doesn't include it)
            # Assuming USER is a separate profile model linked to the user:
            # user_profile = USER(user=user, phone=phone)
            # user_profile.save()

            messages.success(request, 'Sign up successful! You can now log in.')
            return redirect('login')
        except Exception as e:
            messages.error(request, f"Error occurred while signing up: {e}. Please try again.")
    return render(request, 'home/signup.html')

def logout(request):
    request.session.flush()
    messages.info(request, "You have been logged out.")
    return redirect('login')

#User section
def user_home(request):
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    if MERCHANT.objects.filter(userID=user_id):
        ismerchant = 'yes'
        return render(request, 'user/user_home.html', {'ismerchant': ismerchant})
    else:
        ismerchant = None
        return render(request, 'user/user_home.html', {'ismerchant': ismerchant})

def food_list(request):
    user_id = request.session.get('user_id')
    location = request.session.get('location')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    
    return render(request, 'user/food_list.html')

def food_search(request):
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    return render(request, 'user/food_search.html')

def food_premise(request,premiseID):
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    premise = PREMISE.objects.get(premiseID=premiseID)
    
    return render(request, 'user/food_premise.html')

def user_location(request):
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    

    
    return render(request, 'user/user_location.html')

def add_address(request):
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    
    return render(request, 'user/user_location.html')

def catering_list(request):
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    return render(request, 'user/catering_list.html')

def hall_list(request):
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    return render(request, 'user/hall_list.html')

def user_profile(request):
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    user = USER.objects.get(userID=user_id)
    context = {
        'user': user,
    }
    
    return render(request, 'user/user_profile.html', context)

def merchant_register(request):
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    return render(request, 'user/merchant_register.html')

def receipt(request):
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    return render(request, 'user/receipt.html')

def user_update(request):
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    user = USER.objects.get(userID=user_id)
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        phone = request.POST.get('phone')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')

        if password != confirm_password:
            messages.error(request, "Passwords do not match")
            return redirect('user_update')
        else:
            try:
                user.username = username
                user.email = email
                user.phone = phone
                user.save()
                messages.success(request, "User updated successfully")
            
            except Exception as e:
                messages.error(request, "Error updating user")

    context = {
        'user': user,
    }
    
    return render(request,'user/user_update.html', context)

def user_update_password(request):
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    user = USER.objects.get(userID=user_id)
    
    if request.method == 'POST':
        current_password = request.POST.get('current_password')
        new_password = request.POST.get('new_password')
        confirm_new_password = request.POST.get('confirm_new_password')

        if check_password(user.password,current_password):
            messages.error(request, "Current password is incorrect. Try again")
        else:
            if new_password != confirm_new_password:
                messages.error(request, "Passwords do not match. Try again")
            else:
                try:
                    user.password = make_password(new_password)
                    user.save()
                    messages.success(request, "Password updated successfully")
                except Exception as e:
                    messages.error(request, f"Error updating password. {e}")


    
    return render(request,'user/user_update_password.html')