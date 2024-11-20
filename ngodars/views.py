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
    """
    View to display food list based on user's selected location
    """
    user_id = request.session.get('user_id')
    location_data = request.session.get('locations')
    
    # Check user authentication and type
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    # Handle search functionality
    if request.method == 'GET':
        search = request.GET.get('search_query', '')
        if search:
            return redirect('food_search', search_query=search)
    
    try:
        user = USER.objects.get(userID=user_id)
        context = {'user': user}
        
        # Get the actual address object from database if location is selected
        if location_data:
            try:
                address_obj = ADDRESS.objects.get(
                    userID=user,
                    is_used=True
                )
                context['address'] = address_obj
                
                # Get premises based on postcode
                premises = PREMISE.objects.filter(poscode=location_data['poscode'])
                premise_type = PREMISE.objects.filter(premisetype='food')
                context['premise_type'] = premise_type
                context['premises'] = premises
                context['location'] = address_obj
            except ADDRESS.DoesNotExist:
                # Handle case where address doesn't exist anymore
                request.session['locations'] = None
                premises = PREMISE.objects.all()
                context['premises'] = premises
                messages.info(request, "Selected address not found. Showing all available restaurants.")
        else:
            # No address selected - show all premises
            premises = PREMISE.objects.all()
            context['premises'] = premises
        
        return render(request, 'user/food_list.html', context)
        
    except USER.DoesNotExist:
        messages.error(request, "User not found. Please login again")
        return redirect('login')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('user_location')
        
    

def food_search(request, search_query):
    user_id = request.session.get('user_id')
    location_data = request.session.get('locations')
    
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    try:
        user = USER.objects.get(userID=user_id)
        context = {'user': user}
        
        # Case-insensitive search using __icontains
        premises = PREMISE.objects.filter(
            premisename__icontains=search_query, 
            premisetype='food'
        )
        
        # Add location context if available
        if location_data:
            try:
                address_obj = ADDRESS.objects.get(
                    userID=user,
                    is_used=True
                )
                context['location'] = address_obj
            except ADDRESS.DoesNotExist:
                request.session['locations'] = None
        
        context.update({
            'premises': premises,
            'search_query': search_query
        })
        
        return render(request, 'user/food_search.html', context)
        
    except USER.DoesNotExist:
        messages.error(request, "User not found. Please login again")
        return redirect('login')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('user_location')

def food_premise(request,premiseID):
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    premise = PREMISE.objects.get(premiseID=premiseID)
    
    return render(request, 'user/food_premise.html')

def user_location(request):
    """
    View to display and manage user addresses
    """
    # Check user authentication and type
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    try:
        # Retrieve the user object
        user = USER.objects.get(userID=user_id)
        
        # Retrieve addresses for the user
        addresses = ADDRESS.objects.filter(userID=user)
        
        # Check if there's a currently used address
        used_address = addresses.filter(is_used=True).first()
        
        context = {
            'addresses': addresses,
            'used_address_id': used_address.addressID if used_address else None
        }

        # Store only necessary address data in session
        if used_address:
            request.session['locations'] = {
                'addressID': used_address.addressID,
                'poscode': used_address.poscode,
                'streetname': used_address.streetname,
                'statearea': used_address.statearea,
                'unit': used_address.unit,
                'fullname': used_address.fullname
            }
        else:
            request.session['locations'] = None
        
        return render(request, 'user/user_location.html', context)
        
    except USER.DoesNotExist:
        messages.error(request, "User not found. Please login again")
        return redirect('login')

def use_address(request, address_id):
    """
    View to handle marking an address as used
    """
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        
        try:
            # Get the user
            user = USER.objects.get(userID=user_id)
            
            # Reset all addresses for this user to not used
            ADDRESS.objects.filter(userID=user).update(is_used=False)
            
            # Get the specific address
            address = ADDRESS.objects.get(addressID=address_id, userID=user)
            
            # Mark this address as used
            address.is_used = True
            address.save()
            
            # Store postcode in session for premises filtering
            request.session['location_postcode'] = address.poscode
            
            messages.success(request, "Address marked as used successfully")
            return redirect('user_location')
        
        except USER.DoesNotExist:
            messages.error(request, "User not found")
        except ADDRESS.DoesNotExist:
            messages.error(request, "Address not found")
        
        return redirect('user_location')

def delete_address(request, address_id):
    """
    View to handle address deletion
    """
    if request.method == 'POST':
        user_id = request.session.get('user_id')
        
        try:
            # Get the user
            user = USER.objects.get(userID=user_id)
            
            # Get the specific address
            address = ADDRESS.objects.get(addressID=address_id, userID=user)
            
            # Remove from session if this was the used address
            if request.session.get('used_address_id') == address_id:
                del request.session['used_address_id']
            
            # Delete the address
            address.delete()
            
            messages.success(request, "Address deleted successfully")
        
        except USER.DoesNotExist:
            messages.error(request, "User not found")
        except ADDRESS.DoesNotExist:
            messages.error(request, "Address not found")
        
        return redirect('user_location')

def add_address(request):
    # Check if user is logged in via session
    user_id = request.session.get('user_id')
    
    # Verify user type and authentication
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to add address. Please login again.")
        return redirect('login')
    
    if request.method == 'POST':
        # Extract form data
        fullname = request.POST.get('fullname')
        unit = request.POST.get('unit')
        streetname = request.POST.get('streetname')
        statearea = request.POST.get('statearea')
        poscode = request.POST.get('poscode')
        
        # Validate input
        if not all([fullname, unit, streetname, statearea, poscode]):
            messages.error(request, "Please fill in all fields.")
            return render(request, 'user/add_address.html')
        
        try:
            # Retrieve the user object
            user = USER.objects.get(userID=user_id)
            
            # Create new address
            new_address = ADDRESS.objects.create(
                fullname=fullname,
                unit=unit,
                streetname=streetname,
                statearea=statearea,
                poscode=poscode,
                userID=user
            )
            
            # Success message and redirect
            messages.success(request, "Address added successfully!")
        
        except USER.DoesNotExist:
            messages.error(request, "User not found. Please login again.")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"An error occurred: {str(e)}")
    
    # GET request
    return render(request, 'user/add_address.html')

def catering_list(request):
    """
    View to display food list based on user's selected location
    """
    user_id = request.session.get('user_id')
    location_data = request.session.get('locations')
    
    # Check user authentication and type
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    # Handle search functionality
    if request.method == 'GET':
        search = request.GET.get('search_query', '')
        if search:
            return redirect('catering_search', search_query=search)
    
    try:
        user = USER.objects.get(userID=user_id)
        context = {'user': user}
        
        # Get the actual address object from database if location is selected
        if location_data:
            try:
                address_obj = ADDRESS.objects.get(
                    userID=user,
                    is_used=True
                )
                context['address'] = address_obj
                
                # Get premises based on postcode
                premises = PREMISE.objects.filter(poscode=location_data['poscode'])
                premise_type = PREMISE.objects.filter(premisetype='catering')
                context['premise_type'] = premise_type
                context['premises'] = premises
                context['location'] = address_obj
            except ADDRESS.DoesNotExist:
                # Handle case where address doesn't exist anymore
                request.session['locations'] = None
                premises = PREMISE.objects.all()
                context['premises'] = premises
                messages.info(request, "Selected address not found. Showing all available restaurants.")
        else:
            # No address selected - show all premises
            premises = PREMISE.objects.all()
            context['premises'] = premises
        
        return render(request, 'user/catering_list.html', context)
        
    except USER.DoesNotExist:
        messages.error(request, "User not found. Please login again")
        return redirect('login')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('user_location')
   

def catering_search(request, search_query):
    user_id = request.session.get('user_id')
    location_data = request.session.get('locations')
    
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    try:
        user = USER.objects.get(userID=user_id)
        context = {'user': user}
        
        # Case-insensitive search using __icontains
        premises = PREMISE.objects.filter(
            premisename__icontains=search_query, 
            premisetype='catering'
        )
        
        # Add location context if available
        if location_data:
            try:
                address_obj = ADDRESS.objects.get(
                    userID=user,
                    is_used=True
                )
                context['location'] = address_obj
            except ADDRESS.DoesNotExist:
                request.session['locations'] = None
        
        context.update({
            'premises': premises,
            'search_query': search_query
        })
        
        return render(request, 'user/catering_search.html', context)
        
    except USER.DoesNotExist:
        messages.error(request, "User not found. Please login again")
        return redirect('login')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('user_location')

    
    

def hall_list(request):
    """
    View to display food list based on user's selected location
    """
    user_id = request.session.get('user_id')
    location_data = request.session.get('locations')
    
    # Check user authentication and type
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    # Handle search functionality
    if request.method == 'GET':
        search = request.GET.get('search_query', '')
        if search:
            return redirect('hall_search', search_query=search)
    
    try:
        user = USER.objects.get(userID=user_id)
        context = {'user': user}
        
        # Get the actual address object from database if location is selected
        if location_data:
            try:
                address_obj = ADDRESS.objects.get(
                    userID=user,
                    is_used=True
                )
                context['address'] = address_obj
                
                # Get premises based on postcode
                premises = PREMISE.objects.filter(poscode=location_data['poscode'])
                premise_type = PREMISE.objects.filter(premisetype='hall')
                context['premise_type'] = premise_type
                context['premises'] = premises
                context['location'] = address_obj
            except ADDRESS.DoesNotExist:
                # Handle case where address doesn't exist anymore
                request.session['locations'] = None
                premises = PREMISE.objects.all()
                context['premises'] = premises
                messages.info(request, "Selected address not found. Showing all available restaurants.")
        else:
            # No address selected - show all premises
            premises = PREMISE.objects.all()
            context['premises'] = premises
        
        return render(request, 'user/hall_list.html', context)
        
    except USER.DoesNotExist:
        messages.error(request, "User not found. Please login again")
        return redirect('login')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('user_location')
    
def hall_search(request, search_query):
    user_id = request.session.get('user_id')
    location_data = request.session.get('locations')
    
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    try:
        user = USER.objects.get(userID=user_id)
        context = {'user': user}
        
        # Case-insensitive search using __icontains
        premises = PREMISE.objects.filter(
            premisename__icontains=search_query, 
            premisetype='hall'
        )
        
        # Add location context if available
        if location_data:
            try:
                address_obj = ADDRESS.objects.get(
                    userID=user,
                    is_used=True
                )
                context['location'] = address_obj
            except ADDRESS.DoesNotExist:
                request.session['locations'] = None
        
        context.update({
            'premises': premises,
            'search_query': search_query
        })
        
        return render(request, 'user/hall_search.html', context)
        
    except USER.DoesNotExist:
        messages.error(request, "User not found. Please login again")
        return redirect('login')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('user_location')

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
    
    if request.method == 'POST':
        action = request.POST.get('action')
        if action == 'accept':
            # Get the user object
            user = USER.objects.get(userID=user_id)
            
            # Create new merchant with the same name as user
            merchant = MERCHANT.objects.create(
                merchantname=user.username,
                userID=user
            )
            merchant.save()
            
            messages.success(request, "Successfully registered as a merchant!")
            return redirect('merchant_dashboard')
        else:
            return redirect('user_home')
    
    return render(request, 'user/merchant_register.html')

def receipt(request):
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    bookings = BOOKING.objects.all().order_by('-datetime')
    return render(request, 'user/receipt.html', {
        'bookings': bookings,
        'user_id': user_id,
        'ismerchant': request.session.get('ismerchant', 'no')
    })

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

# merchant section
def merchant_dashboard(request):
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    return render(request,'merchant/merchant_dashboard.html')