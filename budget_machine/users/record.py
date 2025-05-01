
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
import os
import json
from datetime import datetime
from django.conf import settings
class Record:
    @login_required(login_url='sign_in')
    def welcome(request):
        user = request.user
        capitalized_name = user.first_name.title()
        user_id = user.id

        # Default values
        total_balance = 0
        total_budget = 0
        average_spent = 0

        # File path
        user_data_folder = os.path.join(settings.BASE_DIR, 'user_data')
        user_file_path = os.path.join(user_data_folder, f"{user_id}.json")

        if os.path.exists(user_file_path):
            with open(user_file_path, 'r') as file:
                user_data = json.load(file)

            # Read total_balance from file
            total_balance = user_data.get('total_balance', 0)

            # Ensure today's date exists
            today_date = datetime.now().strftime("%Y-%m-%d")
            if today_date not in user_data:
                user_data[today_date] = {
                    "record": "Present",
                    "food_price": 0,
                    "traspotation_price": 0,
                    "bill_price": 0,
                    "other_price": 0,
                    "total_expense": 0
                }
                with open(user_file_path, 'w') as file:
                    json.dump(user_data, file, indent=4)

            # Calculate total of all expenses
            all_expenses = [
                value.get('total_expense', 0)
                for key, value in user_data.items()
                if isinstance(value, dict) and 'total_expense' in value
            ]
            total_expenses_sum = sum(all_expenses)

            # Recalculate total_budget
            total_budget = total_balance - total_expenses_sum

            # Calculate average daily spending
            if all_expenses:
                average_spent = round(total_expenses_sum / len(all_expenses), 2)

        # Greeting message
        now = datetime.now()
        current_hour = now.hour
        if current_hour < 12:
            greeting = "Good Morning"
        elif current_hour < 18:
            greeting = "Good Afternoon"
        else:
            greeting = "Good Evening"

        return render(request, "welcome.html", {
            "user": user,
            "name": capitalized_name,
            "greeting": greeting,
            "total_balance": total_balance,
            "total_budget": total_budget,
            "average_spent": average_spent,
        })


    @login_required(login_url='sign_in')
    def view_all_records(request):
        user = request.user
        user_id = user.id
        user_data_folder = os.path.join(settings.BASE_DIR, 'user_data')
        user_file_path = os.path.join(user_data_folder, f"{user_id}.json")

        # Initialize variables to store the records
        records_data = {}

        if os.path.exists(user_file_path):
            with open(user_file_path, 'r') as file:
                user_data = json.load(file)

                # Check if today's date exists in records and add it
                today_date = datetime.now().strftime("%Y-%m-%d")
                for date, details in user_data.items():
                    if date != "total_balance" and date != "total_budget":  # Skip the main balance data
                        records_data[date] = details

        return render(request, "view_all_records.html", {"records_data": records_data})
    
    @login_required(login_url='sign_in')
    def add_budget(request):
        if request.method == "POST":
            added_amount = int(request.POST.get('budget', 0))

            user = request.user
            user_id = user.id

            user_data_folder = os.path.join(settings.BASE_DIR, 'user_data')
            user_file_path = os.path.join(user_data_folder, f"{user_id}.json")

            if os.path.exists(user_file_path):
                with open(user_file_path, 'r') as file:
                    user_data = json.load(file)

                # 👇 Add amount to total_balance (Total amount added)
                user_data['total_balance'] = user_data.get('total_balance', 0) + added_amount

                # 👇 Also add to total_budget (Remaining balance)
                user_data['total_budget'] = user_data.get('total_budget', 0) + added_amount

                with open(user_file_path, 'w') as file:
                    json.dump(user_data, file, indent=4)

            return redirect('welcome')  # Go back to welcome page after adding budget

        return render(request, "add_budget.html")
    
    @login_required(login_url='sign_in')
    def withdraw_amount(request):
        if request.method == "POST":
            withdraw_value = int(request.POST.get('amount', 0))

            user = request.user
            user_id = user.id

            user_data_folder = os.path.join(settings.BASE_DIR, 'user_data')
            user_file_path = os.path.join(user_data_folder, f"{user_id}.json")

            if os.path.exists(user_file_path):
                with open(user_file_path, 'r') as file:
                    user_data = json.load(file)

                total_budget = user_data.get('total_budget', 0)

                if withdraw_value > total_budget:
                    # ❌ Withdrawal is greater than remaining balance
                    return render(request, "withdraw_amount.html", {
                        "error": "Cannot withdraw more than your remaining balance."
                    })

                # ✅ Proceed with withdrawal
                user_data['total_balance'] = max(0, user_data.get('total_balance', 0) - withdraw_value)
                user_data['total_budget'] = max(0, total_budget - withdraw_value)

                with open(user_file_path, 'w') as file:
                    json.dump(user_data, file, indent=4)

            return redirect('welcome')  # after withdrawing, go back to welcome page

        return render(request, "withdraw_amount.html")
    
    @login_required(login_url='sign_in')
    def transaction(request):
        user = request.user
        user_id = user.id
        user_data_folder = os.path.join(settings.BASE_DIR, 'user_data')
        user_file_path = os.path.join(user_data_folder, f"{user_id}.json")

        # Get user's current balance
        current_balance = 0
        if os.path.exists(user_file_path):
            with open(user_file_path, 'r') as file:
                user_data = json.load(file)
                current_balance = user_data.get('total_balance', 0)

        if request.method == "POST":
            # Get the transaction values from the form
            food_price = int(request.POST.get('food_price', 0))
            traspotation_price = int(request.POST.get('traspotation_price', 0))
            bill_price = int(request.POST.get('bill_price', 0))
            other_price = int(request.POST.get('other_price', 0))

            total_transaction_amount = food_price + traspotation_price + bill_price + other_price

            # Check if total transaction amount is greater than the current balance
            if total_transaction_amount > current_balance:
                error_message = "Total transaction amount cannot exceed your current balance."
                return render(request, "transaction.html", {"error": error_message})

            # If the amount is valid, update the record for today's date
            today_date = datetime.now().strftime("%Y-%m-%d")

            if os.path.exists(user_file_path):
                with open(user_file_path, 'r') as file:
                    user_data = json.load(file)

                # Update today's record or add a new one
                if today_date not in user_data:
                    user_data[today_date] = {
                        "food_price": food_price,
                        "traspotation_price": traspotation_price,
                        "bill_price": bill_price,
                        "other_price": other_price,
                        "total_expense": total_transaction_amount
                    }
                else:
                    user_data[today_date]["food_price"] += food_price
                    user_data[today_date]["traspotation_price"] += traspotation_price
                    user_data[today_date]["bill_price"] += bill_price
                    user_data[today_date]["other_price"] += other_price
                    user_data[today_date]["total_expense"] += total_transaction_amount

                # Deduct the total transaction amount from the current balance and budget
                user_data['total_budget'] -= total_transaction_amount

                # Save the updated user data back to the file
                with open(user_file_path, 'w') as file:
                    json.dump(user_data, file, indent=4)

                return redirect('welcome')  # Redirect back to the welcome page

        return render(request, "transaction.html")
    
    @login_required(login_url='sign_in')
    def view_transaction_chart(request):
        # Get the current user
        user = request.user
        user_id = user.id

        # Path to the user's JSON data file
        user_data_folder = os.path.join(settings.BASE_DIR, 'user_data')
        user_file_path = os.path.join(user_data_folder, f"{user_id}.json")

        # Load data from the JSON file if it exists
        if os.path.exists(user_file_path):
            with open(user_file_path, 'r') as file:
                user_data = json.load(file)
        
            # Get daily data and categories (food, transport, bills, etc.)
            daily_data = {key: value for key, value in user_data.items() if key != 'total_balance' and key != 'total_budget'}
            categories = ['food_price', 'traspotation_price', 'bill_price', 'other_price']
            total_balance = user_data.get('total_balance', 0)
            total_budget = user_data.get('total_budget', 0)
        else:
            # Handle the case when the JSON file doesn't exist (or is corrupted)
            daily_data = {}
            categories = []
            total_balance = 0
            total_budget = 0

        # Pass the data to the template
        return render(request, 'transaction_chart.html', {
            'daily_data': json.dumps(daily_data),
            'categories': json.dumps(categories),
            'total_balance': total_balance,
            'total_budget': total_budget,
        })