from django.contrib.auth import authenticate, login, logout
from django.http import JsonResponse
import json
from market.models import Customer


def register_customer(request):
    if request.method != 'POST':
        payload = {"message": "Username already exists. (or other messages)"}
        return JsonResponse(status=400, data=payload)

    try:
        data = request.read().decode('ascii')
        customer_data = json.loads(data)
        customer = Customer.register(customer_data)
        payload = {"id": customer.id}
        return JsonResponse(status=201, data=payload)
    except:
        payload = {"message": "Username already exists. (or other messages)"}
        return JsonResponse(status=400, data=payload)


def customer_list(request):
    if request.method != 'GET':
        payload = {"message": "Username already exists. (or other messages)"}
        return JsonResponse(status=400, data=payload)

    try:
        word = request.GET.get("search")
        customers_data = Customer.search(word=word)
        customers = []
        for item in customers_data:
            customers.append({"id": item.id, "username": item.user.username, "first_name": item.user.first_name,
                              "last_name": item.user.last_name, "email": item.user.email, "phone": item.phone,
                              "address": item.address, "balance": item.balance})
        payload = {"customers": customers}
        return JsonResponse(status=200, data=payload)

    except:
        payload = {"message": "Username already exists. (or other messages)"}
        return JsonResponse(status=400, data=payload)


def customer_information(request, customer_id):
    if request.method != 'GET':
        payload = {"message": "Username already exists. (or other messages)"}
        return JsonResponse(status=400, data=payload)

    try:
        customer = Customer.get_customer(customer_id)
        payload = {"id": customer.id, "username": customer.user.username, "first_name": customer.user.first_name,
                   "last_name": customer.user.last_name, "email": customer.user.email, "phone": customer.phone,
                   "address": customer.address, "balance": customer.balance}
        return JsonResponse(status=200, data=payload)
    except:
        payload = {"message": "Customer Not Found."}
        return JsonResponse(status=404, data=payload)


def edit_customer(request, customer_id):
    if request.method != 'POST':
        payload = {"message": "Username already exists. (or other messages)"}
        return JsonResponse(status=400, data=payload)
    try:
        customer = Customer.get_customer(customer_id)

    except:
        payload = {"message": "Customer Not Found."}
        return JsonResponse(status=404, data=payload)

    try:
        acceptable_items = ["first_name", "last_name", "email", "phone", "address", "balance"]
        forbidden_items = ["id", "username", "password"]
        data = request.read().decode('ascii')
        new_information = json.loads(data)

        for item in new_information:
            if item in forbidden_items:
                payload = {"message": "Cannot edit customer's identity and credentials."}
                return JsonResponse(status=403, data=payload)

        for item in new_information:
            if item in acceptable_items:
                if item == "first_name":
                    customer.user.first_name = new_information['first_name']
                    customer.user.save()

                elif item == "email":
                    customer.user.email = new_information['email']
                    customer.user.save()

                elif item == "last_name":
                    customer.user.last_name = new_information['last_name']
                    customer.user.save()

                elif item == "phone":
                    customer.phone = new_information['phone']
                    customer.save()

                elif item == "address":
                    customer.address = new_information['address']
                    customer.save()

                elif item == "balance":
                    customer.balance = new_information['balance']
                    customer.save()

            else:
                payload = {"message": "Balance should be integer. (or other messages)"}
                return JsonResponse(status=400, data=payload)

        payload = {"id": customer.id, "username": customer.user.username, "first_name": customer.user.first_name,
                   "last_name": customer.user.last_name, "email": customer.user.email, "phone": customer.phone,
                   "address": customer.address, "balance": customer.balance}
        return JsonResponse(status=200, data=payload)
    except:
        payload = {"message": "Balance should be integer. (or other messages)"}
        return JsonResponse(status=400, data=payload)


def login_customer(request):
    if request.method != 'POST':
        payload = {"message": "Username already exists. (or other messages)"}
        return JsonResponse(status=400, data=payload)
    try:
        data = request.read().decode('ascii')
        dic_data = json.loads(data)
        username = dic_data.get('username')
        password = dic_data.get('password')
        user = authenticate(request, username=username, password=str(password))

        if user is not None:
            login(request, user)
            payload = {"message": "You are logged in successfully."}
            return JsonResponse(status=200, data=payload)
        else:
            payload = {"message": "Username or Password is incorrect."}
            return JsonResponse(status=404, data=payload)
    except:
        payload = {"message": "Balance should be integer. (or other messages)"}
        return JsonResponse(status=400, data=payload)


def logout_customer(request):
    if request.method != 'POST':
        payload = {"message": "Username already exists. (or other messages)"}
        return JsonResponse(status=400, data=payload)

    try:
        if request.user.is_authenticated:
            logout(request)
            payload = {"message": "You are logged out successfully."}
            return JsonResponse(status=200, data=payload)
        else:
            payload = {"message": "You are not logged in."}
            return JsonResponse(status=403, data=payload)
    except:
        payload = {"message": "Balance should be integer. (or other messages)"}
        return JsonResponse(status=400, data=payload)


def customer_profile(request):
    if request.method != 'GET':
        payload = {"message": "Username already exists. (or other messages)"}
        return JsonResponse(status=400, data=payload)

    try:
        if request.user.is_authenticated:
            customer = Customer.get_customer(request.user.id)
            payload = {"id": customer.id, "username": customer.user.username, "first_name": customer.user.first_name,
                       "last_name": customer.user.last_name, "email": customer.user.email, "phone": customer.phone,
                       "address": customer.address, "balance": customer.balance}
            return JsonResponse(status=200, data=payload)
        else:
            payload = {"message": "You are not logged in."}
            return JsonResponse(status=403, data=payload)

    except:
        payload = {"message": "Balance should be integer. (or other messages)"}
        return JsonResponse(status=400, data=payload)
