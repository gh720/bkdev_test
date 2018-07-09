from django.core.exceptions import ValidationError
from django.db import models, connection
from django.db.models import Max, F, Value
from django.db.models.functions import Coalesce
import datetime
from django.utils import timezone

from core.helpers import auto_str, Round, checked_value

GENDER_CHOICES = [('M', 'M'), ('F', 'F')]


class DiscountManager(models.Manager):

    def __init__(self, current_time=None):
        super().__init__()
        self.current_time = current_time

    def discounted_on_the_fly(self, now=None):
        if now is None:
            now = timezone.now()
        result = Product.objects.all().annotate(
            started=Coalesce('category__productdiscount__started',
                             datetime.date(1900, 1, 1))
            , ended=Coalesce('category__productdiscount__ended',
                             datetime.date(2100, 1, 1))
            , amount=Value('category__productdiscount__amount')
        ).filter(started__lte=now, ended__gt=now
                 ).values('id', 'name', 'price', 'effective_discount_id'
                          ).annotate(
            discount_amount=Max('category__productdiscount__amount'))
        return result

    def discounted(self):
        result = Product.objects.all().annotate(
            eff_price=Round(Coalesce(
                F('price') - F('price') * F('effective_discount__amount') / 100,
                F('price')))
            , disc_value=Round(
                Coalesce(F('price') * F('effective_discount__amount') / 100, 0))
        )
        return result

    def check_discounts(self):
        for prod in Product.objects.all():
            expected_discount = prod.category_eff_disc()
            if (expected_discount is None) != (prod.effective_discount is None) \
                    or (expected_discount is not None
                        and abs(expected_discount.amount
                                - prod.effective_discount.amount) > 0.0001):
                print(
                    "effective discount computed incorrectly: %s:\n expected=%s,\n is=%s" % (
                        prod, expected_discount, prod.effective_discount))

    def compute_product_discounts(self):
        with connection.cursor() as cr:
            cr.execute('''
            update core_product p set effective_discount_id=q.eff_id
            from (
                select distinct pc_pc.product_id
                , first_value(dc_d.amount) over(partition by pc_pc.product_id 
                        order by dc_d.amount desc,dc_d.ctid asc ) eff_value
                , first_value(dc_d.id) over(partition by pc_pc.product_id 
                        order by dc_d.amount desc,dc_d.ctid asc ) eff_id
                from core_productdiscount_category dc
                    join core_product_category dc_pc on dc_pc.category_id=dc.category_id
                    join core_product_category pc_pc on dc_pc.product_id=pc_pc.product_id
                    join core_productdiscount_category pc_dc on pc_dc.category_id=pc_pc.category_id
                    join core_productdiscount dc_d on dc_d.id=pc_dc.productdiscount_id
                where 1=1
                and coalesce(dc_d.started, date('1900-01-01')) <= %s
                and coalesce(dc_d.ended, date('2100-01-01')) > %s
            )q
            where p.id=q.product_id
            ''', [timezone.now(), timezone.now()])
            rc = cr.rowcount
            print("*** rowcount: %s" % (rc))


@auto_str
class Customer(models.Model):
    name = models.CharField(max_length=200)
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, null=True,
                              blank=True)


@auto_str
class Category(models.Model):
    name = models.CharField(max_length=200)
    parent_category = models.ForeignKey("self", null=True, blank=True,
                                        on_delete=models.SET_NULL)
    assignable = models.BooleanField(default=True)



@auto_str
class Product(models.Model):
    name = models.CharField(max_length=200)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ManyToManyField(Category, related_name="products")
    effective_discount = models.ForeignKey("ProductDiscount", null=True,
                                           blank=True,
                                           related_name="discounted_products"
                                           , on_delete=models.SET_NULL)

    objects = DiscountManager()

    # django does not allow us to validate m2m fields on create yet
    # validation should be implemented in forms

    @property
    def effective_price(self):
        discount_value = self.discount_value
        eff_price = self.price - self.discount_value
        if eff_price < 0 or eff_price > self.price:
            return self.price
        return eff_price

    @property
    def discount_value(self):
        if self.effective_discount is None:
            return 0
        discount_value = checked_value(
            round(self.price * self.effective_discount.amount / 100, 2)
            , 0, self.price, 0)
        return discount_value

    def category_eff_disc(self, now=None):
        ''' dumb discount calculation, only to double check '''
        max_amount, eff_disc = 0, None
        if now is None:
            now = timezone.now()
        for category in self.category.all():
            for disc in category.productdiscount_set.all():
                if (disc.started is None or disc.started <= now
                ) and (disc.ended is None or disc.ended > now):
                    amount = disc.amount or 0
                    if max_amount < amount:
                        max_amount = amount
                        eff_disc = disc

        return eff_disc

    def category_str(self):
        return ";".join([p.name for p in self.category.all()])


class BaseDiscount(models.Model):
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    started = models.DateTimeField(null=True)
    ended = models.DateTimeField(null=True)
    comment = models.CharField(max_length=200, blank=True, null=True)

    class Meta:
        abstract = True

    def active(self, now=None):
        if now is None:
            now = timezone.now()
        if self.started is None or self.started <= now:
            if self.ended is None or self.ended > now:
                return True
        return False


@auto_str
class CustomerDiscount(BaseDiscount):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)


@auto_str
class ProductDiscount(BaseDiscount):
    category = models.ManyToManyField(Category, blank=True)

    def category_str(self):
        return ";".join([p.name for p in self.category.all()])


@auto_str
class CartItem(models.Model):
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    customer_discount = models.ForeignKey(CustomerDiscount, null=True,
                                          blank=True, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    product_count = models.IntegerField()

    @property
    def discount_value(self):
        prod_discount_amount = (lambda d: d and d.amount or 0)(
            self.product.effective_discount)
        cust_discount_amount = (lambda d: d and d.amount or 0)(
            self.customer_discount)
        discount_value = checked_value(
            self.product.price * max(prod_discount_amount,
                                     cust_discount_amount) / 100
            , 0, self.product.price, 0)
        return discount_value * self.product_count

    @property
    def effective_price(self):
        discounted_price = self.product.price - self.discount_value
        return discounted_price * self.product_count

    def clean(self):
        if (self.customer_discount is not None
            and self.customer_discount not in self.customer.customerdiscount_set.all()):
            raise ValidationError(
                "Please, choose the discount that is available for this customer")

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

