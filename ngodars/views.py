from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib import messages
from datetime import datetime, timedelta
from django.http import JsonResponse, HttpResponseRedirect
from django.urls import reverse
from django.db.models import Q
from django.utils import timezone
from ngodars.models import USER, MERCHANT, ADDRESS, PREMISE, ITEM, BOOKING
from django.contrib.auth.hashers import make_password, check_password
import json
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth
from django.core.exceptions import ValidationError
import os

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

def food_premise(request, premise_id):
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    premise = PREMISE.objects.get(premiseID=premise_id)
    
    # Get all items for this premise
    items = ITEM.objects.filter(premiseID=premise)
    
    # Handle item selection and booking
    if request.method == 'POST':
        selected_item_id = request.POST.get('item_id')
        
        try:
            selected_item = ITEM.objects.get(itemID=selected_item_id)
            # Redirect to payment page using premise ID and selected item ID
            return redirect('food_payment', premise_id=premise.premiseID, item_id=selected_item.itemID)
        
        except ITEM.DoesNotExist:
            messages.error(request, "Selected item does not exist.")
    
    context = {
        'premise': premise,
        'items': items
    }
    
    return render(request, 'user/food_premise.html', context)
    
def catering_premise(request, premise_id):
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    premise = PREMISE.objects.get(premiseID=premise_id)
    
    # Get all items for this premise
    items = ITEM.objects.filter(premiseID=premise)
    
    # Handle item selection and booking
    if request.method == 'POST':
        selected_item_id = request.POST.get('item_id')
        
        try:
            selected_item = ITEM.objects.get(itemID=selected_item_id)
            # Redirect to payment page using premise ID and selected item ID
            return redirect('catering_payment', premise_id=premise.premiseID, item_id=selected_item.itemID)
        
        except ITEM.DoesNotExist:
            messages.error(request, "Selected item does not exist.")
    
    context = {
        'premise': premise,
        'items': items
    }
    
    return render(request, 'user/catering_premise.html', context)

def hall_premise(request, premise_id):
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    premise = PREMISE.objects.get(premiseID=premise_id)
    
    # Get all items for this premise
    items = ITEM.objects.filter(premiseID=premise)
    
    # Handle item selection and booking
    if request.method == 'POST':
        selected_item_id = request.POST.get('item_id')
        
        try:
            selected_item = ITEM.objects.get(itemID=selected_item_id)
            # Redirect to payment page using premise ID and selected item ID
            return redirect('hall_payment', premise_id=premise.premiseID, item_id=selected_item.itemID)
        
        except ITEM.DoesNotExist:
            messages.error(request, "Selected item does not exist.")
    
    context = {
        'premise': premise,
        'items': items
    }
    
    return render(request, 'user/hall_premise.html', context)


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
    
    bookings = BOOKING.objects.filter(userID=user_id).order_by('-datetime')
    if MERCHANT.objects.filter(userID=user_id):
        ismerchant = 'yes'
    return render(request, 'user/receipt.html', {
        'bookings': bookings,
        'user_id': user_id,
        'ismerchant': ismerchant,
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
    # Verify merchant authentication
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    # Get the current merchant
    try:
        merchant = MERCHANT.objects.get(userID=user_id)
    except MERCHANT.DoesNotExist:
        messages.error(request, "Merchant profile not found.")
        return redirect('user_home')
    
    # Aggregate sales by quantity and revenue per month
    monthly_sales = BOOKING.objects.filter(
        itemID__premiseID__merchantID=merchant
    ).annotate(
        month=TruncMonth('datetime')
    ).values('month').annotate(
        total_quantity=Count('bookingID'),
        total_revenue=Sum('itemID__price')
    ).order_by('month')
    
    # Generate dynamic months (last 6 months)
    current_date = datetime.now()
    
    # If no sales data, generate empty months
    if not monthly_sales:
        months = [(current_date - timedelta(days=30*i)).strftime('%B %Y') for i in range(5, -1, -1)]
        quantities = [0] * 6
        revenues = [0.0] * 6
    else:
        # Process existing sales data
        months = [sale['month'].strftime('%B %Y') for sale in monthly_sales]
        quantities = [sale['total_quantity'] for sale in monthly_sales]
        revenues = [float(sale['total_revenue']) for sale in monthly_sales]
        
        # Ensure we always have 6 months of data
        while len(months) < 6:
            # Add missing months at the beginning
            previous_month = datetime.strptime(months[0], '%B %Y') - timedelta(days=30)
            months.insert(0, previous_month.strftime('%B %Y'))
            quantities.insert(0, 0)
            revenues.insert(0, 0.0)
    
    context = {
        'merchant': merchant,
        'months': json.dumps(months),
        'quantities': json.dumps(quantities),
        'revenues': json.dumps(revenues),
    }
    
    return render(request, 'merchant/merchant_dashboard.html', context)

def premise(request):
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    # Retrieve premises for the current merchant
    merchant = MERCHANT.objects.get(userID=user_id)
    premises = PREMISE.objects.filter(merchantID=merchant)
    
    return render(request, 'merchant/premise.html', {'premises': premises})

def add_premise(request):
    # Authentication check
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    if request.method == 'POST':
        # Get the current logged-in merchant
        user_id = request.session.get('user_id')
        try:
            user = USER.objects.get(userID=user_id)
            merchant = MERCHANT.objects.get(userID=user)
            
            # Collect form data
            premise_data = {
                'premisename': request.POST.get('premisename'),
                'premisetype': request.POST.get('premisetype'),
                'streetname': request.POST.get('streetname'),
                'unit': request.POST.get('unit'),
                'poscode': request.POST.get('poscode'),
                'statearea': request.POST.get('statearea'),
                'merchantID': merchant,
                'premiseimage': request.FILES.get('premiseimage')
            }
            
            # Create and save the premise
            premise = PREMISE(**premise_data)
            premise.save()
            
            messages.success(request, "Premise added successfully!")
        
        except (USER.DoesNotExist, MERCHANT.DoesNotExist) as e:
            messages.error(request, "Error: Unable to find merchant account.")
            return redirect('login')
    
    return render(request, 'merchant/add_premise.html')


def update_premise(request, premise_id):
    # Check if user is logged in and is a merchant
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    # Get the premise or return 404 if not found
    premise = get_object_or_404(PREMISE, premiseID=premise_id)
    
    # Verify that the premise belongs to the current merchant
    merchant = MERCHANT.objects.get(userID=user_id)
    if premise.merchantID != merchant:
        messages.error(request, "You are not authorized to update this premise")
        return redirect('premise')
    
    if request.method == 'POST':
        try:
            # Update premise details
            premise.premisename = request.POST.get('premisename')
            premise.premisetype = request.POST.get('premisetype')
            premise.streetname = request.POST.get('streetname')
            premise.unit = request.POST.get('unit')
            premise.poscode = request.POST.get('poscode')
            premise.statearea = request.POST.get('statearea')
            
            # Update image if a new one is uploaded
            if request.FILES.get('premiseimage'):
                # Validate image
                premise.premiseimage = request.FILES['premiseimage']
            
           
            premise.save()
            
            messages.success(request, "Premise updated successfully!")
        
        except ValidationError as e:
            # Handle validation errors
            messages.error(request, str(e))
    
    # Render the update premise template
    return render(request, 'merchant/update_premise.html', {
        'premise': premise
    })

def delete_premise(request, premise_id):
    # Check if user is logged in and is a merchant
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to perform this action. Please login again")
        return redirect('login')
    
    try:
        # Get the premise or return 404 if not found
        premise = get_object_or_404(PREMISE, premiseID=premise_id)
        
        # Verify that the premise belongs to the current merchant
        merchant = MERCHANT.objects.get(userID=user_id)
        if premise.merchantID != merchant:
            messages.error(request, "You are not authorized to delete this premise")
            return redirect('premise')
        
        # Check if the premise has any associated items
        associated_items = ITEM.objects.filter(premiseID=premise)
        if associated_items.exists():
            messages.error(request, "Cannot delete premise. There are items associated with this premise.")
            return redirect('premise')
        
        # Delete the premise image file if it exists
        if premise.premiseimage:
            try:
                os.remove(premise.premiseimage.path)
            except Exception as file_error:
                # Log the file deletion error but continue with database deletion
                messages.error(f"Error deleting premise image: {file_error}")
        
        # Delete the premise
        premise.delete()
        
        # Add success message
        messages.success(request, f"Premise '{premise.premisename}' deleted successfully!")
        
        return redirect('premise')
    
    except MERCHANT.DoesNotExist:
        messages.error(request, "Merchant account not found")
        return redirect('login')
    
    except Exception as e:
        # Catch any unexpected errors
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('premise')
    
def items(request):
    # Check if user is logged in and is a merchant
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    try:
        # Get the current merchant
        merchant = MERCHANT.objects.get(userID=user_id)
        
        # Retrieve all premises for this merchant
        premises = PREMISE.objects.filter(merchantID=merchant)
        
        # Prepare premises with item count
        premises_with_items = []
        for premise in premises:
            item_count = ITEM.objects.filter(premiseID=premise).count()
            premises_with_items.append({
                'premise': premise,
                'item_count': item_count,
                'full_address': f"{premise.streetname}, {premise.unit or 'N/A'}, {premise.poscode} {premise.statearea}"
            })
        
        return render(request, 'merchant/items.html', {
            'premises_with_items': premises_with_items
        })
    
    except MERCHANT.DoesNotExist:
        messages.error(request, "Merchant account not found")
        return redirect('login')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('merchant_dashboard')
    
def premise_items(request, premise_id):
    # Check if user is logged in and is a merchant
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to view this page. Please login again")
        return redirect('login')
    
    try:
        # Get the premise or return 404 if not found
        premise = get_object_or_404(PREMISE, premiseID=premise_id)
        
        # Verify that the premise belongs to the current merchant
        merchant = MERCHANT.objects.get(userID=user_id)
        if premise.merchantID != merchant:
            messages.error(request, "You are not authorized to view these items")
            return redirect('items')
        
        # Retrieve all items for this premise
        items = ITEM.objects.filter(premiseID=premise)
        
        return render(request, 'merchant/premise_items.html', {
            'premise': premise,
            'items': items
        })
    
    except MERCHANT.DoesNotExist:
        messages.error(request, "Merchant account not found")
        return redirect('login')
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('items')
    
def add_item(request, premise_id):
    # [MODIFIED] Added comprehensive user authentication and permission check
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to add items. Please login again.")
        return redirect('login')

    try:
        # Get the premise or return 404 if not found
        premise = get_object_or_404(PREMISE, premiseID=premise_id)
        
        # Verify that the premise belongs to the current merchant
        merchant = MERCHANT.objects.get(userID=user_id)
        if premise.merchantID != merchant:
            messages.error(request, "You are not authorized to add items to this premise.")
            return redirect('items')

        if request.method == 'POST':
            # [NEW] Item creation with validation
            item_name = request.POST.get('itemname')
            price = request.POST.get('price')
            item_image = request.FILES.get('itemimage')

            # Validation checks
            if not item_name:
                messages.error(request, "Item name is required.")
                return render(request, 'merchant/add_item.html', {'premise': premise})

            try:
                price = float(price)
                if price < 0:
                    raise ValueError("Price cannot be negative")
            except ValueError:
                messages.error(request, "Invalid price. Please enter a valid number.")
                return render(request, 'merchant/add_item.html', {'premise': premise})

            # Create new item
            new_item = ITEM(
                itemname=item_name,
                price=price,
                itemimage=item_image,
                premiseID=premise
            )

            try:
                new_item.full_clean()  # Validate model constraints
                new_item.save()
                messages.success(request, f"Item '{item_name}' added successfully!")
                return redirect('premise_items', premise_id=premise.premiseID)
            
            except ValidationError as e:
                messages.error(request, f"Validation error: {str(e)}")
                return render(request, 'merchant/add_item.html', {'premise': premise})

        return render(request, 'merchant/add_item.html', {'premise': premise})

    except MERCHANT.DoesNotExist:
        messages.error(request, "Merchant account not found")
        return redirect('login')
    
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('items')

def update_item(request, item_id):
    # Check if user is logged in and is a merchant
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to update items")
        return redirect('login')
    
    try:
        # Get the item or return 404 if not found
        item = ITEM.objects.get(itemID=item_id)
        
        # Verify that the item's premise belongs to the current merchant
        merchant = MERCHANT.objects.get(userID=user_id)
        if item.premiseID.merchantID != merchant:
            messages.error(request, "You are not authorized to update this item")
            return redirect('items')
        
        if request.method == 'POST':
            try:
                # Update item details
                item.itemname = request.POST.get('itemname')
                item.price = request.POST.get('price')
                
                # Handle image update
                if request.FILES.get('itemimage'):
                    # Validate image
                    item.validate_image(request.FILES['itemimage'])
                    item.itemimage = request.FILES['itemimage']

                premise_id = item.premiseID.premiseID

                item.save()
                
                messages.success(request, f"Item '{item.itemname}' updated successfully!")
                return redirect('premise_items', premise_id=item.premiseID.premiseID)
            
            except ValidationError as e:
                messages.error(request, str(e))
        
        return render(request, 'merchant/update_item.html', {
            'item': item
        })
    
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('items')

def delete_item(request, item_id):
    # [MODIFIED] Added comprehensive user authentication and permission check
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to delete items. Please login again.")
        return redirect('login')

    try:
        # Get the item or return 404 if not found
        item = ITEM.objects.get(itemID=item_id)
        
        # Verify that the item belongs to a premise of the current merchant
        merchant = MERCHANT.objects.get(userID=user_id)
        if item.premiseID.merchantID != merchant:
            messages.error(request, "You are not authorized to delete this item.")
            return redirect('items')

        # Store premise for redirection
        premise_id = item.premiseID.premiseID
        
        # Delete the item
        item_name = item.itemname  # Store name before deletion
        item.delete()
        
        messages.success(request, f"Item '{item_name}' deleted successfully!")
        return redirect('premise_items', premise_id=premise_id)

    except MERCHANT.DoesNotExist:
        messages.error(request, "Merchant account not found")
        return redirect('login')
    
    except Exception as e:
        messages.error(request, f"An error occurred: {str(e)}")
        return redirect('items')

def food_payment(request, premise_id, item_id):
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to delete items. Please login again.")
        return redirect('login')

    # Fetch the premise and item details
    premise = PREMISE.objects.get(premiseID=premise_id)
    item = ITEM.objects.get(itemID=item_id)
    user = USER.objects.get(userID=user_id)

    if request.method == 'POST':
        # Process the payment (this is just a placeholder for actual payment processing logic)
        card_number = request.POST.get('card_number')
        expiry_date = request.POST.get('expiry_date')
        cvv = request.POST.get('cvv')

        # Here you would normally handle payment processing logic
        # For example, calling a payment gateway API

        # Simulate payment success
        payment_successful = True  # Replace this with actual payment processing result

        if payment_successful:
            # Create a booking record
            booking = BOOKING(
                userID=user,  # Assuming you have a user field in your Booking model
                itemID=item,
                payment='paid',  # Or whatever status you want to set
                datetime = timezone.now()
            )
            booking.save()
            messages.success(request, 'Payment successful! Your booking has been confirmed.')
            return redirect('food_list')  # Redirect to a success page or user home
        else:
            messages.error(request, 'Payment failed. Please try again.')

    return render(request, 'user/food_payment.html', {'premise': premise, 'item': item})

def catering_payment(request, premise_id, item_id):
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to delete items. Please login again.")
        return redirect('login')

    # Fetch the premise and item details
    premise = PREMISE.objects.get(premiseID=premise_id)
    item = ITEM.objects.get(itemID=item_id)
    user = USER.objects.get(userID=user_id)

    if request.method == 'POST':
        # Process the payment (this is just a placeholder for actual payment processing logic)
        card_number = request.POST.get('card_number')
        expiry_date = request.POST.get('expiry_date')
        cvv = request.POST.get('cvv')

        # Here you would normally handle payment processing logic
        # For example, calling a payment gateway API

        # Simulate payment success
        payment_successful = True  # Replace this with actual payment processing result

        if payment_successful:
            # Create a booking record
            booking = BOOKING(
                userID=user,  # Assuming you have a user field in your Booking model
                itemID=item,
                payment='paid',  # Or whatever status you want to set
                datetime = timezone.now()
            )
            booking.save()
            messages.success(request, 'Payment successful! Your booking has been confirmed.')
            return redirect('catering_list')  # Redirect to a success page or user home
        else:
            messages.error(request, 'Payment failed. Please try again.')

    return render(request, 'user/catering_payment.html', {'premise': premise, 'item': item})

def hall_payment(request, premise_id, item_id):
    user_id = request.session.get('user_id')
    if not request.session.get('user_type') == 'user':
        request.session.flush()
        messages.error(request, "You do not have permission to delete items. Please login again.")
        return redirect('login')

    # Fetch the premise and item details
    premise = PREMISE.objects.get(premiseID=premise_id)
    item = ITEM.objects.get(itemID=item_id)
    user = USER.objects.get(userID=user_id)

    if request.method == 'POST':
        # Process the payment (this is just a placeholder for actual payment processing logic)
        card_number = request.POST.get('card_number')
        expiry_date = request.POST.get('expiry_date')
        cvv = request.POST.get('cvv')

        # Here you would normally handle payment processing logic
        # For example, calling a payment gateway API

        # Simulate payment success
        payment_successful = True  # Replace this with actual payment processing result

        if payment_successful:
            # Create a booking record
            booking = BOOKING(
                userID=user,  # Assuming you have a user field in your Booking model
                itemID=item,
                payment='paid',  # Or whatever status you want to set
                datetime = timezone.now()
            )
            booking.save()
            messages.success(request, 'Payment successful! Your booking has been confirmed.')
            return redirect('hall_list')  # Redirect to a success page or user home
        else:
            messages.error(request, 'Payment failed. Please try again.')

    return render(request, 'user/hall_payment.html', {'premise': premise, 'item': item})