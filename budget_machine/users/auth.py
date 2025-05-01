from django.contrib.auth import update_session_auth_hash
from django.http import HttpResponse
from django.contrib.auth.models import User
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login , logout 
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_http_methods
from datetime import datetime
from django.conf import settings
import os
import json
class Auth:
    
    @staticmethod
    def sign_in(request):
        if request.method == "POST":
            email = request.POST.get("email").lower()
            password = request.POST.get("password")

            # Check if email exists
            try:
                user = User.objects.get(email=email)
            except User.DoesNotExist:
                return render(request, "sign_in.html", {"error": "Email does not exist."})

            # Authenticate using username (Django uses username by default)
            user = authenticate(request, username=user.username, password=password)
            
            if user is not None:
                login(request, user)
                return redirect("welcome") 
            else:
                return render(request, "sign_in.html", {"error": "Incorrect password."})

        return render(request, "sign_in.html")
    @staticmethod
    def sign_up(request):
        if request.method == "POST":
            name = request.POST.get("name").lower()
            email = request.POST.get("email").lower()
            password = request.POST.get("password")
            confirm_password = request.POST.get("confirm_password")

            # 1. Check if username already exists
            if User.objects.filter(username=name).exists():
                return render(request, "sign_up.html", {"error": "Username already taken."})

            # 2. Check if email already exists
            if User.objects.filter(email=email).exists():
                return render(request, "sign_up.html", {"error": "Email already registered."})

            # 3. Password match check
            if password != confirm_password:
                return render(request, "sign_up.html", {"error": "Passwords do not match."})

            # 4. Create user
            user = User.objects.create_user(username=name, email=email, password=password, first_name=name)
            user.save()

            # Refresh user to ensure ID is assigned
            user = User.objects.get(username=name)

            # 5. Create user_data folder inside MEDIA_ROOT (or project root)
            user_data_folder = os.path.join(settings.BASE_DIR, 'user_data')
            os.makedirs(user_data_folder, exist_ok=True)

            date = datetime.now().strftime("%Y-%m-%d")

            # 6. Create JSON file
            initial_data = {
                "total_balance": 0,
                "total_budget": 0,
                f"{date}": {
                    "food_price": 0,
                    "traspotation_price": 0,
                    "bill_price": 0,
                    "other_price": 0,
                    "total_expense": 0
                }
            }

            user_file_path = os.path.join(user_data_folder, f"{user.id}.json")
            with open(user_file_path, 'w') as file:
                json.dump(initial_data, file, indent=4)

            return redirect("welcome")

        return render(request, "sign_up.html")

    @login_required(login_url='sign_in')
    def delete_user( request):
        user = request.user  # Get the currently logged-in user
        # Construct the path to the user's JSON data file
        json_file_path = os.path.join(settings.BASE_DIR, 'user_data', f'{user.id}.json')
        # Delete the JSON file if it exists
        if os.path.exists(json_file_path):
            os.remove(json_file_path)
        # Delete the user account
        user.delete()

        return redirect('home')
        

    @login_required(login_url='sign_in')
    def update_profile(request):
        user = request.user

        if request.method == "POST":
            name = request.POST.get("name").strip().lower()
            email = request.POST.get("email").strip().lower()
            current_password = request.POST.get("current_password")
            new_password = request.POST.get("new_password")

            # Check current password
            if not user.check_password(current_password):
                return render(request, "update_profile.html", {"error": "Incorrect current password.", "user": user})

            changes_made = False

            # Update name if changed and not empty
            if name and name != user.first_name:
                user.first_name = name
                user.username = name  # Optional: If you want username same as name
                changes_made = True

            # Update email if changed and not empty
            if email and email != user.email:
                if User.objects.filter(email=email).exclude(id=user.id).exists():
                    return render(request, "update_profile.html", {"error": "Email already in use.", "user": user})
                user.email = email
                changes_made = True

            # Update password if new_password provided
            if new_password:
                user.set_password(new_password)
                update_session_auth_hash(request, user)  # Keep user logged in after password change
                changes_made = True

            if changes_made:
                user.save()
                return render(request, "update_profile.html", {"success": "Profile updated successfully.", "user": user})
            else:
                return redirect("welcome")

        return render(request, "update_profile.html", {"user": user})      
    
    @csrf_exempt
    @require_http_methods(["GET", "POST"])
    def sign_out(request):
        logout(request)
        if request.headers.get("Accept") == "*/*":  # Beacon case
            return HttpResponse("Logged out via beacon", status=200)
        return redirect("sign_in")