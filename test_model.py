import datetime
import os
import sys
from json import encoder

import django
from django.utils import timezone

os.environ['DJANGO_SETTINGS_MODULE'] = 'punchbag.settings'
django.setup()

from core.models import Product, ProductDiscount, Category, CartItem, Customer

try:
    prod5 = Product.objects.create(name="Молоток test1", price=100)
    prod5.category.add(Category.objects.get(id=18))
    prod5.refresh_from_db()
    # print ("effective discount: %s " % (prod5.effective_discount))
    assert prod5.effective_price == 90, "expected: 90, is: %s" % (
    prod5.effective_price)
    Product.objects.check_discounts()
    print("ok: category to product assignment")

    disc1 = ProductDiscount.objects.create(amount=15
                                           ,
                                           started=timezone.now() - datetime.timedelta(
                                               days=1)
                                           ,
                                           ended=timezone.now() + datetime.timedelta(
                                               days=31)
                                           , comment="test1"
                                           )
    cat1 = Category.objects.create(name=prod5.name + ": распродажа test1"
                                   , parent_category=Category.objects.get(id=10)
                                   , assignable=True)

    prod5.category.add(cat1)
    prod5.refresh_from_db()
    assert prod5.effective_price == 90, "expected: 90, is: %s" % (
    prod5.effective_price)
    Product.objects.check_discounts()

    disc1.category.add(cat1)
    prod5.refresh_from_db()
    assert prod5.effective_price == 85, "expected: 85, is: %s" % (
    prod5.effective_price)
    Product.objects.check_discounts()
    print("ok: discount creation and assignment")

    disc1.category.remove(cat1)
    prod5.refresh_from_db()
    assert prod5.effective_price == 90, "expected: 90, is: %s" % (
    prod5.effective_price)
    Product.objects.check_discounts()
    print("ok: discount-category relation removal")

    disc1.category.add(cat1)
    prod5.refresh_from_db()
    assert prod5.effective_price == 85, "expected: 85, is: %s" % (
    prod5.effective_price)
    Product.objects.check_discounts()

    disc1.amount = 30
    disc1.save()
    # prod5.refresh_from_db() won't refresh ForeignKey
    prod5 = Product.objects.all().filter(name__contains="test1").first()
    assert prod5.effective_price == 70, "expected: 70, is: %s" % (
    prod5.effective_price)
    Product.objects.check_discounts()
    print("ok: discount amount change")

    disc1.ended = timezone.now() - datetime.timedelta(days=1)
    disc1.save()
    prod5 = Product.objects.all().filter(name__contains="test1").first()
    assert prod5.effective_price == 90, "expected: 90, is: %s" % (
    prod5.effective_price)
    Product.objects.check_discounts()
    print("ok: discount expiration")

    prod5.category.remove(cat1)
    prod5.refresh_from_db()
    assert prod5.effective_price == 90, "expected: 90, is: %s" % (
    prod5.effective_price)
    Product.objects.check_discounts()
    print("ok: product-category relation removal")

finally:
    ProductDiscount.objects.filter(comment__contains="test1").delete()
    Category.objects.filter(name__contains="test1").delete()
    Product.objects.filter(name__contains="test1").delete()

# checking calculation correctness

prod1dr = Product.objects.all().filter(name__contains="Фен")[0]
prod2vc = Product.objects.all().filter(name__contains="Пылесос")[0]
prod3fc = Product.objects.all().filter(name__contains="Шуба")[0]
prod4nb = Product.objects.all().filter(name__contains="Ноутбук")[0]

cust1 = Customer.objects.get(name='Alice')
cust2 = Customer.objects.get(name='Bob')
cust3 = Customer.objects.get(name='Charlie')

print("%-10s buys %-10s: %10s %10s %10s %10s %10s " % (
'X', 'Y', 'price', 'eff. price', 'eff. discount', 'final price',
'final discount'))

for prod in [prod1dr, prod2vc, prod3fc, prod4nb]:
    for cust in [cust1, cust2, cust3]:
        cust_disc = cust.customerdiscount_set.order_by('id').first()

        cartitem = CartItem.objects.create(customer=cust, product=prod,
                                           product_count=1
                                           , customer_discount=cust_disc)

        print("%-10s buys %-10s: %10s %10s %10s %10s %10s " % (
            cust.name, prod.name
            , prod.price
            , prod.effective_price
            , prod.discount_value
            , cartitem.effective_price
            , cartitem.discount_value
        ))

        cartitem.delete()

print("EVERYTHING IS OK")
