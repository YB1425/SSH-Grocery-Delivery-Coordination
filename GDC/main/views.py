# main/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import SharedCart, CartItem, GroceryItem, Notification
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import UserActionHistory

def update_item_price_and_availability(item_name):
    # Placeholder for supermarket API integration
    import random
    price = round(random.uniform(1.0, 10.0), 2)
    availability = random.choice([True, False])
    return price, availability

@login_required
def shared_cart_view(request, cart_id):
    cart = get_object_or_404(SharedCart, id=cart_id, users=request.user)
    search_query = request.GET.get('q', '')  # Get the search query
    items = cart.items.select_related('item').all()

    if search_query:  # Filter items if a search query is provided
        items = items.filter(item__name__icontains=search_query)

    total_price = cart.total_cost()
    split_price = cart.split_cost()
    context = {
        'cart': cart,
        'items': items,
        'total_price': total_price,
        'split_price': split_price,
        'search_query': search_query,
    }
    return render(request, 'shared_cart.html', context)



@login_required
def add_item(request, cart_id):
    cart = get_object_or_404(SharedCart, id=cart_id, users=request.user)
    search_query = request.GET.get('q', '')  # Capture the search query
    available_items = GroceryItem.objects.filter(availability=True)  # Only available items

    if search_query:  # Filter items based on the search query
        available_items = available_items.filter(name__icontains=search_query)

    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        grocery_item = get_object_or_404(GroceryItem, id=item_id)

        # Add the item to the cart
        cart_item = CartItem.objects.create(
            cart=cart,
            item=grocery_item,
            quantity=quantity,
            added_by=request.user
        )

        # Log the action in UserActionHistory
        UserActionHistory.objects.create(
            user=request.user,
            cart=cart,
            item=grocery_item,
            action_type="ADD",
            quantity=quantity,
            details=f"Added {quantity} of {grocery_item.name} to cart {cart.name}."
        )

        # Notify other users
        other_users = cart.users.exclude(id=request.user.id)
        for user in other_users:
            Notification.objects.create(
                user=user,
                message=f"{request.user.username} added {quantity} x {grocery_item.name} to {cart.name}"
            )

        messages.success(request, f'Item "{grocery_item.name}" added successfully.')
        return redirect('add_item', cart_id=cart.id)

    return render(request, 'add_item.html', {'cart': cart, 'available_items': available_items})




@login_required
def remove_item(request, cart_id, item_id):
    cart = get_object_or_404(SharedCart, id=cart_id, users=request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    if request.method == 'POST':
        item_name = cart_item.item.name
        quantity = cart_item.quantity  # Use cart_item's quantity
        cart_item.delete()

        UserActionHistory.objects.create(
            user=request.user,
            cart=cart,
            item=cart_item.item,
            action_type="REMOVE",
            quantity=quantity,
            details=f"Removed {quantity} of {item_name} from cart {cart.name}."
        )

        # Notify other users
        other_users = cart.users.exclude(id=request.user.id)
        for user in other_users:
            Notification.objects.create(
                user=user,
                message=f"{request.user.username} removed {item_name} from {cart.name}"
            )
        messages.success(request, 'Item removed successfully.')
        return redirect('shared_cart', cart_id=cart.id)
    return render(request, 'remove_item.html', {'cart': cart, 'cart_item': cart_item})


@login_required
def modify_item(request, cart_id, item_id):
    cart = get_object_or_404(SharedCart, id=cart_id, users=request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', cart_item.quantity))
        cart_item.quantity = quantity
        cart_item.save()
        # Notify other users
        item_name = cart_item.item.name
        other_users = cart.users.exclude(id=request.user.id)
        for user in other_users:
            Notification.objects.create(
                user=user,
                message=f"{request.user.username} updated {item_name} quantity to {quantity} in {cart.name}"
            )
        messages.success(request, 'Item updated successfully.')
        return redirect('shared_cart', cart_id=cart.id)
    return render(request, 'modify_item.html', {'cart': cart, 'cart_item': cart_item})

def notifications_view(request):
    # Fetching unread notifications in descending order based on the 'created_at' timestamp
    notifications = request.user.notifications.filter(is_read=False).order_by('-created_at')
    context = {'notifications': notifications}
    return render(request, 'notifications.html', context)

@login_required
def mark_notification_read(request, notification_id):
    notification = get_object_or_404(Notification, id=notification_id, user=request.user)
    notification.is_read = True
    notification.save()
    return redirect('notifications')

@login_required
def home(request):
    # Get all shared carts the user is part of
    shared_carts = request.user.shared_carts.all()
    context = {
        'shared_carts': shared_carts,
    }
    return render(request, 'home.html', context)

@login_required
def create_cart(request):
    if request.method == 'POST':
        cart_name = request.POST.get('cart_name')
        if cart_name:
            cart = SharedCart.objects.create(name=cart_name)
            cart.users.add(request.user)
            messages.success(request, f'Shared cart "{cart_name}" created successfully.')
            return redirect('home')
        else:
            messages.error(request, 'Please provide a name for the cart.')
    return render(request, 'create_cart.html')

def register(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Log the user in after successful registration
            login(request, user)
            messages.success(request, 'Registration successful.')
            return redirect('home')  # Redirect to the home page
        else:
            messages.error(request, 'Registration failed. Please correct the errors below.')
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})

def profile(request):
    return render(request, 'profile.html')

def custom_logout(request):
    if request.method == 'POST':  # Ensure security for logout
        logout(request)  # Logs out the user
        return render(request, 'logout.html')  # Render goodbye message
    elif request.method == 'GET':  # Redirect to a safe URL for unsupported methods
        return redirect('home')
    
@login_required
def user_history(request):
    history = request.user.action_history.select_related("cart", "item").order_by("-timestamp")
    return render(request, 'user_history.html', {'history': history})

def get_frequent_items(user):
    from django.db.models import Count
    return UserActionHistory.objects.filter(user=user, action_type="ADD").values(
        "item__name"
    ).annotate(total=Count("id")).order_by("-total")[:5]
