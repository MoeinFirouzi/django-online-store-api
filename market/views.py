import datetime
import json

from django.http import JsonResponse

from market.models import Product, Order


def product_insert(request):
    # hint: you should check request method like below
    if request.method != 'POST':
        payload = {'message': 'Duplicate code (or other messages)'}
        return JsonResponse(status=400, data=payload)

    try:
        data = request.POST
        if 'inventory' in data.keys():
            new_product = Product(code=data['code'], name=data['name'], price=int(data['price']),
                                  inventory=int(data['inventory']))
        else:
            new_product = Product(code=data['code'], name=data['name'], price=int(data['price']))
        new_product.save()
        payload = {"id": new_product.id}
        return JsonResponse(status=201, data=payload)

    except:

        payload = {'message': 'Duplicate code (or other messages)'}
        return JsonResponse(status=400, data=payload)


def product_list(request):
    if request.method != 'GET':
        payload = {'message': 'Duplicate code (or other messages)'}
        return JsonResponse(status=400, data=payload)

    try:
        if len(request.GET) == 0:
            data = Product.objects.all()
            data_list = list()
            for item in data:
                data_list.append({"id": item.id, "code": item.code, "name": item.name,
                                  "price": item.price, "inventory": item.inventory})
            payload = {'products': data_list}
        else:
            search = request.GET['search']
            data = Product.objects.filter(name__contains=search)
            data_list = list()
            for item in data:
                data_list.append({"id": item.id, "code": item.code, "name": item.name,
                                  "price": item.price, "inventory": item.inventory})
            payload = {'products': data_list}
        return JsonResponse(payload)

    except:
        payload = {'message': 'Duplicate code (or other messages)'}
        return JsonResponse(status=400, data=payload)


def product_information(request, product_id):
    if request.method != 'GET':
        payload = {'message': 'Duplicate code (or other messages)'}
        return JsonResponse(status=400, data=payload)
    try:
        product = Product.objects.get(pk=product_id)
        payload = {"id": product.id, "code": product.code, "name": product.name,
                   "price": product.price, "inventory": product.inventory}
        return JsonResponse(payload)
    except:
        payload = {'message': "Product Not Found."}
        return JsonResponse(status=404, data=payload)


def edit_inventory(request, product_id):
    if request.method != 'POST':
        payload = {'message': 'Duplicate code (or other messages)'}
        return JsonResponse(status=400, data=payload)
    try:

        if Product.objects.filter(pk=product_id).exists():
            amount = int(request.POST['amount'])
            product = Product.objects.get(pk=product_id)
            if amount >= 0:
                product.increase_inventory(amount)
            else:
                amount = -1 * amount
                product.decrease_inventory(amount)

            payload = {"id": product.id, "code": product.code, "name": product.name,
                       "price": product.price, "inventory": product.inventory}
            return JsonResponse(payload, status=200)
        else:
            payload = {'message': "Product Not Found."}
            return JsonResponse(status=404, data=payload)
    except:
        payload = {'message': 'Duplicate code (or other messages)'}
        return JsonResponse(status=400, data=payload)


def customer_cart(request):
    if request.user.is_authenticated:
        data = Order.get_order(user=request.user)
        items = []
        for item in data[0]:
            items.append({"code": item.product.code, "name": item.product.name, "price": item.product.price
                             , "amount": item.amount})

        payload = {"total_price": data[1].total_price, "items": items}
        status_code = 200
    else:
        payload = {"message": "You are not logged in."}
        status_code = 403
    return JsonResponse(status=status_code, data=payload)


def add_items(request):
    global product
    if request.user.is_authenticated:
        data = request.read().decode('ascii')
        products_data = json.loads(data)
        rows = Order.get_order(user=request.user)[0]
        order = Order.get_order(request.user)[1]
        error_status = False
        errors, items = [], []
        for item in products_data:
            try:
                product = Product.get_product(code=item['code'])
                if not product:
                    raise Exception("Product not found.")
                order.add_product(product, int(item['amount']))
            except Exception as e:
                error_status = True
                error = str(e)
                errors.append({"code": item['code'], "message": error})

        for item in rows:
            items.append({"code": item.product.code, "name": item.product.name, "price": item.product.price,
                          "amount": item.amount})

        if error_status:
            payload = {"total_price": order.total_price, "errors": errors, "items": items}
            status_code = 400
        else:
            payload = {"total_price": order.total_price, "items": items}
            status_code = 200
    else:
        payload = {"message": "You are not logged in."}
        status_code = 403
    return JsonResponse(status=status_code, data=payload)


def remove_items(request):
    if request.user.is_authenticated:
        data = request.read().decode('ascii')
        products_data = json.loads(data)
        rows, order = Order.get_order(user=request.user)
        errors, items = [], []
        error_status = False
        for item in products_data:
            try:
                product = Product.get_product(code=item['code'])
                if not product:
                    raise Exception("Product not found.")
                order.remove_product(product=product, amount=item.get('amount'))
            except Exception as e:
                error_status = True
                error = str(e)
                errors.append({"code": item['code'], "message": error})

        for item in rows:
            items.append({"code": item.product.code, "name": item.product.name, "price": item.product.price,
                          "amount": item.amount})

        if error_status:
            payload = {"total_price": order.total_price, "errors": errors, "items": items}
            status_code = 400
        else:
            payload = {"total_price": order.total_price, "items": items}
            status_code = 200
    else:
        status_code = 403
        payload = {"message": "You are not logged in."}
    return JsonResponse(status=status_code, data=payload)


def submit(request):
    try:
        if request.user.is_authenticated:
            rows, order = Order.get_order(user=request.user)
            order.submit()
            rows_list = []
            for item in rows:
                rows_list.append({"code": item.product.code, "name": item.product.name, "price": item.product.price,
                                  "amount": item.amount})
            order_time = order.order_time.strftime("%Y-%m-%d %H:%M:%S")

            payload = {"id": order.id, "order_time": order_time,
                       "status": "submitted", "total_price": order.total_price, "rows": rows_list}
            status_code = 200
        else:
            status_code = 403
            payload = {"message": "You are not logged in."}
    except Exception as e:
        status_code = 400
        payload = {"message": str(e)}

    return JsonResponse(status=status_code, data=payload)
