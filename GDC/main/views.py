# main/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import SharedCart, CartItem, GroceryItem, Notification
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm

def update_item_price_and_availability(item_name):
    # Placeholder for supermarket API integration
    import random
    price = round(random.uniform(1.0, 10.0), 2)
    availability = random.choice([True, False])
    return price, availability

@login_required
def shared_cart_view(request, cart_id):
    cart = get_object_or_404(SharedCart, id=cart_id, users=request.user)
    items = cart.items.select_related('item').all()
    total_price = cart.total_cost()
    split_price = cart.split_cost()
    context = {
        'cart': cart,
        'items': items,
        'total_price': total_price,
        'split_price': split_price
    }
    return render(request, 'shared_cart.html', context)


@login_required
def add_item(request, cart_id):
    cart = get_object_or_404(SharedCart, id=cart_id, users=request.user)
    available_items = GroceryItem.objects.all()  # Fetch all grocery items

    if request.method == 'POST':
        item_id = request.POST.get('item_id')
        quantity = int(request.POST.get('quantity', 1))
        grocery_item = get_object_or_404(GroceryItem, id=item_id)

        # Add the item to the cart
        CartItem.objects.create(
            cart=cart,
            item=grocery_item,
            quantity=quantity,
            added_by=request.user
        )

        # Notify other users in the cart
        other_users = cart.users.exclude(id=request.user.id)
        for user in other_users:
            Notification.objects.create(
                user=user,
                message=f"{request.user.username} added {quantity} x {grocery_item.name} to {cart.name}"
            )

        messages.success(request, f'Item "{grocery_item.name}" added successfully.')
        return redirect('shared_cart', cart_id=cart.id)

    return render(request, 'add_item.html', {'cart': cart, 'available_items': available_items})




@login_required
def remove_item(request, cart_id, item_id):
    cart = get_object_or_404(SharedCart, id=cart_id, users=request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    if request.method == 'POST':
        item_name = cart_item.item.name
        cart_item.delete()
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

@login_required
def notifications_view(request):
    notifications = request.user.notifications.filter(is_read=False)
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