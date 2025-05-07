
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.contrib import messages
import os
import json
from datetime import datetime, date
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

            # Read total_balance and total_budget from file
            total_balance = user_data.get('total_balance', 0)
            total_budget = user_data.get('total_budget', 0)

            # Ensure today's date exists
            today_date = datetime.now().strftime("%Y-%m-%d")
            if today_date not in user_data:
                user_data[today_date] = {
                    "record": "Present",
                    "food_price": 0,
                    'transportation_price': 0,
                    "bill_price": 0,
                    "other_price": 0,
                    "total_expense": 0,
                    "sended": [],
                    "receive": [],
                    "deposit":[],
                    "withdraw":[]
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

                # Update balances
                user_data['total_balance'] = user_data.get('total_balance', 0) + added_amount
                user_data['total_budget'] = user_data.get('total_budget', 0) + added_amount

                # Prepare today's date
                today = datetime.now().strftime("%Y-%m-%d")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Ensure today's entry exists
                if today not in user_data:
                    user_data[today] = {
                        "food_price": 0,
                        'transportation_price': 0,
                        "bill_price": 0,
                        "other_price": 0,
                        "total_expense": 0,
                        "sended": [],
                        "receive": [],
                        "deposit": [],
                        "withdraw": []
                    }

                # Append deposit record
                deposit_note = f"Deposited {added_amount} PKR on {timestamp}"
                user_data[today]['deposit'].append({
                    "amount": added_amount,
                    "timestamp": timestamp,
                    "note": deposit_note
                })

                # Save the updated data
                with open(user_file_path, 'w') as file:
                    json.dump(user_data, file, indent=4)

            return redirect('welcome')  # Go back to welcome page

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
                    return render(request, "withdraw_amount.html", {
                        "error": "Cannot withdraw more than your remaining balance."
                    })

                # Deduct from balances
                user_data['total_balance'] = max(0, user_data.get('total_balance', 0) - withdraw_value)
                user_data['total_budget'] = max(0, total_budget - withdraw_value)

                # Today's date and timestamp
                today = datetime.now().strftime("%Y-%m-%d")
                timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # Ensure today's date key exists
                if today not in user_data:
                    user_data[today] = {
                        "food_price": 0,
                        'transportation_price': 0,
                        "bill_price": 0,
                        "other_price": 0,
                        "total_expense": 0,
                        "sended": [],
                        "receive": [],
                        "deposit": [],
                        "withdraw": []
                    }

                # Append to withdraw log
                withdraw_note = f"Withdrew {withdraw_value} PKR on {timestamp}"
                user_data[today]['withdraw'].append({
                    "amount": withdraw_value,
                    "timestamp": timestamp,
                    "note": withdraw_note
                })

                with open(user_file_path, 'w') as file:
                    json.dump(user_data, file, indent=4)

            return redirect('welcome')

        return render(request, "withdraw_amount.html")
    
    @login_required(login_url='sign_in')
    def record(request):
        user = request.user
        user_id = user.id
        user_data_folder = os.path.join(settings.BASE_DIR, 'user_data')
        user_file_path = os.path.join(user_data_folder, f"{user_id}.json")

        # Set defaults
        current_balance = 0
        today_date = datetime.now().strftime("%Y-%m-%d")
        existing_data = {
            "food_price": 0,
            'transportation_price': 0,
            "bill_price": 0,
            "other_price": 0
        }

        # Load existing data
        if os.path.exists(user_file_path):
            with open(user_file_path, 'r') as file:
                user_data = json.load(file)
                current_balance = user_data.get('total_budget', 0)
                if today_date in user_data:
                    today_data = user_data[today_date]
                    existing_data = {
                        "food_price": today_data.get("food_price", 0),
                        'transportation_price': today_data.get('transportation_price', 0),
                        "bill_price": today_data.get("bill_price", 0),
                        "other_price": today_data.get("other_price", 0)
                    }

        if request.method == "POST":
            food_price = int(request.POST.get('food_price', 0))
            transportation_price = int(request.POST.get('transportation_price', 0))
            bill_price = int(request.POST.get('bill_price', 0))
            other_price = int(request.POST.get('other_price', 0))

            total_record_amount = food_price + transportation_price + bill_price + other_price

            if total_record_amount > current_balance:
                error_message = "Total record amount cannot exceed your current balance."
                return render(request, "record.html", {
                    "error": error_message,
                    "existing_data": existing_data
                })

            if os.path.exists(user_file_path):
                with open(user_file_path, 'r') as file:
                    user_data = json.load(file)

                if today_date not in user_data:
                    user_data[today_date] = {
                        "food_price": food_price,
                        'transportation_price': transportation_price,
                        "bill_price": bill_price,
                        "other_price": other_price,
                        "total_expense": total_record_amount
                    }
                else:
                    user_data[today_date]["food_price"] += food_price
                    user_data[today_date]['transportation_price'] += transportation_price
                    user_data[today_date]["bill_price"] += bill_price
                    user_data[today_date]["other_price"] += other_price
                    user_data[today_date]["total_expense"] += total_record_amount

                user_data['total_budget'] -= total_record_amount

                with open(user_file_path, 'w') as file:
                    json.dump(user_data, file, indent=4)

                return redirect('welcome')

        return render(request, "record.html", {
    "existing_data": existing_data,
    "current_balance": current_balance
})

    @login_required(login_url='sign_in')
    def view_record_chart(request):
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
            categories = ['food_price', 'transportation_price', 'bill_price', 'other_price']
            total_balance = user_data.get('total_balance', 0)
            total_budget = user_data.get('total_budget', 0)
        else:
            # Handle the case when the JSON file doesn't exist (or is corrupted)
            daily_data = {}
            categories = []
            total_balance = 0
            total_budget = 0

        # Pass the data to the template
        return render(request, 'record_chart.html', {
            'daily_data': json.dumps(daily_data),
            'categories': json.dumps(categories),
            'total_balance': total_balance,
            'total_budget': total_budget,
        })
    
    def get_username(request, receiver_id):
        try:
            receiver = User.objects.get(id=receiver_id)
            return JsonResponse({'username': receiver.username})
        except User.DoesNotExist:
            return JsonResponse({'username': None})
    
    @login_required(login_url='sign_in')
    def send_money(request):
        if request.method == "POST":
            sender = request.user
            sender_id = sender.id
            sender_username = sender.username

            data_folder = os.path.join(settings.BASE_DIR, 'user_data')
            sender_file_path = os.path.join(data_folder, f"{sender_id}.json")

            # Load sender data
            if not os.path.exists(sender_file_path):
                return render(request, "send_money.html", {"error": "Sender data not found."})

            with open(sender_file_path, 'r') as file:
                sender_data = json.load(file)

            sender_balance = sender_data.get('total_balance', 0)
            sender_budget = sender_data.get('total_budget', 0)

            # Validate receiver_id and amount
            try:
                receiver_id = int(request.POST.get('receiver_id'))
                amount = int(request.POST.get('amount'))
            except (TypeError, ValueError):
                return render(request, "send_money.html", {"error": "Invalid receiver ID or amount."})

            today = datetime.now().strftime("%Y-%m-%d")
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            if receiver_id == sender_id:
                return render(request, "send_money.html", {"error": "You cannot send money to yourself."})

            if amount > sender_balance or amount > sender_budget:
                return render(request, "send_money.html", {"error": "Insufficient balance or budget."})

            # Check receiver user
            try:
                receiver_user = User.objects.get(id=receiver_id)
            except User.DoesNotExist:
                return render(request, "send_money.html", {"error": "Receiver ID not found."})

            receiver_username = receiver_user.username
            receiver_file_path = os.path.join(data_folder, f"{receiver_id}.json")

            if not os.path.exists(receiver_file_path):
                return render(request, "send_money.html", {"error": "Receiver data file not found."})

            with open(receiver_file_path, 'r') as file:
                receiver_data = json.load(file)

            # Confirmation data for modal or UI
            confirmation_data = {
                'receiver_username': receiver_username,
                'receiver_id': receiver_id,
                'amount': amount
            }

            if request.POST.get("confirm") == "yes":
                # Update sender
                sender_data['total_balance'] -= amount
                sender_data['total_budget'] -= amount
                if sender_data['total_balance'] < 0 or sender_data['total_budget'] < 0:
                    return render(request, "send_money.html", {"error": "Transaction exceeds limits."})

                if today not in sender_data:
                    sender_data[today] = {
                        "food_price": 0,
                        "transportation_price": 0,
                        "bill_price": 0,
                        "other_price": 0,
                        "total_expense": 0,
                        "sended": [],
                        "receive": [],
                        "deposit": [],
                        "withdraw": []
                    }

                sender_data[today]["sended"].append({
                    "receiver_id": receiver_id,
                    "amount": amount,
                    "timestamp": timestamp,
                    "note": f"Sent {amount} to user_id {receiver_id} ({receiver_username}) at {timestamp}"
                })

                # Update receiver
                receiver_data['total_balance'] += amount
                receiver_data['total_budget'] += amount

                if today not in receiver_data:
                    receiver_data[today] = {
                        "food_price": 0,
                        "transportation_price": 0,
                        "bill_price": 0,
                        "other_price": 0,
                        "total_expense": 0,
                        "sended": [],
                        "receive": [],
                        "deposit": [],
                        "withdraw": []
                    }

                receiver_data[today]["receive"].append({
                    "sender_id": sender_id,
                    "amount": amount,
                    "timestamp": timestamp,
                    "note": f"Received {amount} from user_id {sender_id} ({sender_username}) at {timestamp}"
                })

                # Save both files
                with open(sender_file_path, 'w') as file:
                    json.dump(sender_data, file, indent=4)

                with open(receiver_file_path, 'w') as file:
                    json.dump(receiver_data, file, indent=4)

                return render(request, "send_money.html", {"success": "Money sent successfully!"})

            return render(request, "send_money.html", {"confirmation_data": confirmation_data})

        return render(request, "send_money.html")

    @login_required(login_url='sign_in')
    def transaction_history(request):
        user = request.user
        user_id = user.id
        user_data_folder = os.path.join(settings.BASE_DIR, 'user_data')
        user_file_path = os.path.join(user_data_folder, f"{user_id}.json")

        if not os.path.exists(user_file_path):
            return render(request, "transaction_history.html", {"error": "No transaction history found."})

        with open(user_file_path, 'r') as file:
            user_data = json.load(file)

        # Initialize the filtered data for all transaction types
        filtered_data = {
            'withdraw': [],
            'deposit': [],
            'sended': [],
            'received': []
        }

        # Collect withdrawal transactions
        for date, details in user_data.items():
            if isinstance(details, dict) and 'withdraw' in details:
                filtered_data['withdraw'].extend(details['withdraw'])

        # Collect deposit transactions
        for date, details in user_data.items():
            if isinstance(details, dict) and 'deposit' in details:
                filtered_data['deposit'].extend(details['deposit'])

        # Collect sent transactions
        for date, details in user_data.items():
            if isinstance(details, dict) and 'sended' in details:
                filtered_data['sended'].extend(details['sended'])

        # Collect received transactions
        for date, details in user_data.items():
            if isinstance(details, dict) and 'receive' in details:
                filtered_data['received'].extend(details['receive'])

        # Sort all transaction types by timestamp (most recent first)
        filtered_data['withdraw'] = sorted(filtered_data['withdraw'], key=lambda x: x['timestamp'], reverse=True)
        filtered_data['deposit'] = sorted(filtered_data['deposit'], key=lambda x: x['timestamp'], reverse=True)
        filtered_data['sended'] = sorted(filtered_data['sended'], key=lambda x: x['timestamp'], reverse=True)
        filtered_data['received'] = sorted(filtered_data['received'], key=lambda x: x['timestamp'], reverse=True)

        return render(request, "transaction_history.html", {
            "withdraws": filtered_data['withdraw'],
            "deposits": filtered_data['deposit'],
            "sended": filtered_data['sended'],
            "received": filtered_data['received'],
            "name": user.first_name.title()
        })
