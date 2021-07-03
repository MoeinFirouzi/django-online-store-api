from django.contrib.auth.models import User, Permission
from django.db import models
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.utils import timezone


class Product(models.Model):
    code = models.CharField(max_length=10, unique=True, null=True)
    name = models.CharField(max_length=100, null=True)
    price = models.PositiveIntegerField(null=True)
    inventory = models.PositiveIntegerField(default=0)

    def increase_inventory(self, amount):
        if isinstance(amount, int):
            self.inventory += amount
            self.save()
        else:
            raise Exception("Error")

    def decrease_inventory(self, amount):
        if isinstance(amount, int):
            self.inventory -= amount
            self.save()
        else:
            raise Exception("Error")

    @staticmethod
    def get_product(code):
        try:
            product = get_object_or_404(Product, code=code)
        except:
            product = None
        finally:
            return product


class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True)
    phone = models.CharField(max_length=20, null=True)
    address = models.TextField()
    balance = models.PositiveIntegerField(default=20000)

    def deposit(self, amount):
        if isinstance(amount, int):
            self.balance += amount
            self.save()
        else:
            raise Exception("Error")

    def spend(self, amount):
        if isinstance(amount, int):
            self.balance -= amount
            self.save()
        else:
            raise Exception("Error")

    @staticmethod
    def register(user_data):
        new_user = User.objects.create_user(username=user_data['username'], password=user_data['password'],
                                            first_name=user_data['first_name'], last_name=user_data['last_name'],
                                            email=user_data['email'])
        new_user.is_staff = True
        new_user.is_superuser = True
        new_user.save()

        new_customer = Customer.objects.create(user=new_user, phone=user_data['phone'], address=user_data['address'])
        new_customer.save()

        return new_customer

    @staticmethod
    def search(word=None):
        if word is None:
            customers = Customer.objects.all()
            return customers
        else:
            customers = Customer.objects.filter(
                Q(user__username__contains=word) | Q(user__last_name__contains=word) | Q(
                    user__first_name__contains=word) | Q(address__contains=word))
            return customers

    @staticmethod
    def get_customer(customer_id):
        customer = get_object_or_404(Customer, id=customer_id)
        return customer


class OrderRow(models.Model):
    product = models.ForeignKey('Product', on_delete=models.CASCADE, null=True)
    order = models.ForeignKey('Order', related_name='rows', on_delete=models.CASCADE, null=True)
    amount = models.PositiveIntegerField(null=True)

    @staticmethod
    def get_order_row(order, searching_product):
        order_row = OrderRow.objects.get(product=searching_product, order=order)
        return order_row


class Order(models.Model):
    # Status values. DO NOT EDIT
    STATUS_SHOPPING = 1
    STATUS_SUBMITTED = 2
    STATUS_CANCELED = 3
    STATUS_SENT = 4

    status_choices = [(STATUS_SHOPPING, 'در حال خرید'), (STATUS_SUBMITTED, 'ثبت‌شده'),
                      (STATUS_CANCELED, 'لغوشده'), (STATUS_SENT, 'ارسال‌شده')]

    customer = models.ForeignKey('Customer', on_delete=models.PROTECT, null=True)
    order_time = models.DateTimeField(null=True)
    total_price = models.PositiveIntegerField(default=0)
    status = models.IntegerField(choices=status_choices, null=True)

    @staticmethod
    def get_order(user):
        order = Order.objects.filter(customer__user=user).filter(status=Order.STATUS_SHOPPING)
        if len(order) > 0:
            return order[0].rows.all(), order[0]
        else:
            order = Order.initiate(Customer.objects.get(user=user))
            return order.rows.all(), order

    @staticmethod
    def initiate(customer):
        order_data_count = Order.objects.filter(status=1, customer=customer).count()
        if order_data_count == 0:
            order_obj = Order(customer=customer, status=1)
            order_obj.save()
            return order_obj
        elif order_data_count == 1:
            return Order.objects.get(status=1, customer=customer)
        else:
            raise Exception("Error")

    def add_product(self, product, amount):
        object_in_row = OrderRow.objects.filter(product=product, order=self).exists()

        if not object_in_row:
            if 0 < amount <= product.inventory:
                added_product = OrderRow(product=product, amount=amount, order=self)
                added_product.save()

                total = 0
                total += added_product.product.price * amount
                if added_product.amount > added_product.product.inventory:
                    raise Exception("Error")
                self.total_price += total
                self.save()
            else:
                raise Exception("Not enough inventory.")
        else:
            order_row_object = OrderRow.objects.get(order=self, product=product)
            if 0 < amount + order_row_object.amount <= product.inventory:
                order_row_object.amount += amount
                order_row_object.save()

                total = 0
                total += order_row_object.product.price * amount
                if order_row_object.amount > order_row_object.product.inventory:
                    raise Exception("Error")
                self.total_price += total
                self.save()

            else:
                raise Exception("Not enough inventory.")

    def remove_product(self, product, amount=None):
        try:
            order_row_object = OrderRow.objects.get(order=self, product=product)
        except:
            raise Exception("Product not found in cart.")
        try:
            if amount is None or order_row_object.amount - amount == 0:
                self.total_price -= order_row_object.product.price * order_row_object.amount
                self.save()
                order_row_object.delete()

            else:
                if 0 < order_row_object.amount - amount:
                    order_row_object.amount -= amount
                    order_row_object.save()

                    self.total_price -= order_row_object.product.price * amount
                    self.save()
                else:
                    raise Exception("Error.")
        except:
            raise Exception("Not enough amount in cart.")

    def submit(self):
        if self.status != 1 or self.rows.all().count() == 0:
            raise Exception("Not open order found.")

        if self.total_price > self.customer.balance:
            raise Exception("Not enough money.")

        self.customer.spend(self.total_price)

        for i in self.rows.all():
            if i.amount > i.product.inventory:
                raise Exception("Not enough inventory.")

        for i in self.rows.all():
            i.product.decrease_inventory(i.amount)

        self.order_time = timezone.localtime(timezone.now())
        self.status = 2
        self.save()

    def cancel(self):
        if self.status != 2:
            raise Exception("Error")

        for i in self.rows.all():
            i.product.increase_inventory(i.amount)

        self.customer.deposit(self.total_price)
        self.status = 3
        self.save()

    def send(self):
        if self.status != 2:
            raise Exception("Error")
        self.status = 4
        self.save()
