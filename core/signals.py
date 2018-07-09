from django.db import connection
from django.db.models.signals import m2m_changed, post_save
from django.dispatch import receiver
from django.utils import timezone

from core.models import ProductDiscount, Product, Category

@receiver(m2m_changed, sender=ProductDiscount.category.through, dispatch_uid='m2m_productdiscount')
def m2m_productdiscount(sender, instance, action, **kwargs) -> None:
    # print("m2m_productdiscount called: %s, %s" % (action, instance))

    if action in ('pre_remove'):
        instance._products_affected = list(*Product.objects.filter(category__productdiscount=instance).values_list('id'))
        # print ("*** affected %s" % (instance._products_affected))
    elif (action in ('post_add')):
        with connection.cursor() as cr:
            cr.execute('''
                update core_product p set effective_discount_id=q.eff_id
                from (
                    select distinct pc_pc.product_id
                    , first_value(dc_d.amount) over(partition by pc_pc.product_id order by dc_d.amount desc,dc_d.ctid asc ) eff_value
                    , first_value(dc_d.id) over(partition by pc_pc.product_id order by dc_d.amount desc,dc_d.ctid asc ) eff_id
                    from core_productdiscount_category dc
                        join core_product_category dc_pc on dc_pc.category_id=dc.category_id
                        join core_product_category pc_pc on dc_pc.product_id=pc_pc.product_id
                        join core_productdiscount_category pc_dc on pc_dc.category_id=pc_pc.category_id
                        join core_productdiscount dc_d on dc_d.id=pc_dc.productdiscount_id
                    where 1=1
                    and dc.productdiscount_id=%s
                    and coalesce(dc_d.started, date('1900-01-01')) <= %s
                    and coalesce(dc_d.ended, date('2100-01-01')) > %s
                )q
                where p.id=q.product_id
                returning q.eff_id
            ''', [instance.id, timezone.now(), timezone.now()])
            rc = cr.rowcount
            output = cr.fetchone()
            # print ("*** rowcount: %s, eff_id: %s" % (rc, output))
    elif (action in ('post_remove')):
        _products_affected=getattr(instance, '_products_affected', None)
        if _products_affected:
            with connection.cursor() as cr:
                cr.execute('''
                    update core_product p set effective_discount_id=q.eff_id
                    from (
                        select distinct pc.product_id
                        , first_value(dc_d.amount) over(partition by pc.product_id order by dc_d.amount desc,dc_d.ctid asc ) eff_value
                        , first_value(dc_d.id) over(partition by pc.product_id order by dc_d.amount desc,dc_d.ctid asc ) eff_id
                        from core_product_category pc 
                            join core_productdiscount_category dc_pc on dc_pc.category_id=pc.category_id
                            join core_productdiscount dc_d on dc_d.id=dc_pc.productdiscount_id
                        where 1=1
                        and pc.product_id=ANY(%s)
                        and coalesce(dc_d.started, date('1900-01-01')) <= %s
                        and coalesce(dc_d.ended, date('2100-01-01')) > %s
                    )q
                    where p.id=q.product_id
                    returning q.eff_id
                ''', [_products_affected, timezone.now(), timezone.now()])
                rc = cr.rowcount
                output = cr.fetchone()
                # print ("*** rowcount: %s, eff_id: %s" % (rc, output))
                instance._products_affected=None

@receiver(post_save, sender=ProductDiscount, dispatch_uid='update_productdiscount')
def update_productdiscount(sender, instance, **kwargs) -> None:
    # print("update_productdiscount called: %s" % (instance))

    with connection.cursor() as cr:
        cr.execute('''
            update core_product p set effective_discount_id=q.eff_id
            from (
                select distinct pc_pc.product_id
                , first_value(dc_d.amount) over(partition by pc_pc.product_id order by dc_d.amount desc,dc_d.ctid asc ) eff_value
                , first_value(dc_d.id) over(partition by pc_pc.product_id order by dc_d.amount desc,dc_d.ctid asc ) eff_id
                from core_productdiscount_category dc
                    join core_product_category dc_pc on dc_pc.category_id=dc.category_id
                    join core_product_category pc_pc on dc_pc.product_id=pc_pc.product_id
                    join core_productdiscount_category pc_dc on pc_dc.category_id=pc_pc.category_id
                    join core_productdiscount dc_d on dc_d.id=pc_dc.productdiscount_id
                where 1=1
                and dc.productdiscount_id=%s
                and coalesce(dc_d.started, date('1900-01-01')) <= %s
                and coalesce(dc_d.ended, date('2100-01-01')) > %s
            )q
            where p.id=q.product_id
            returning q.eff_id
        ''', [instance.id, timezone.now(), timezone.now()])
        rc = cr.rowcount
        output = cr.fetchone()
        # print ("*** rowcount: %s, eff_id: %s" % (rc, output))



@receiver(m2m_changed, sender=Product.category.through, dispatch_uid='m2m_product')
def m2m_product(sender, instance, action, **kwargs) -> None:
    # print("m2m_product called: %s, %s" % (action, instance))
    if (action in ('post_add', 'post_remove')):
        with connection.cursor() as cr:
            cr.execute('''
                update core_product p set effective_discount_id=q.eff_id
                from (
                    select distinct p.id
                    , first_value(dc_d.amount) over(partition by p.id order by dc_d.amount desc,dc_d.ctid asc ) eff_value
                    , first_value(dc_d.id) over(partition by p.id order by dc_d.amount desc,dc_d.ctid asc ) eff_id
                    from core_product p
                        join core_product_category p_pc on p_pc.product_id=p.id
                        join core_productdiscount_category pc_dc on pc_dc.category_id=p_pc.category_id
                        join core_productdiscount dc_d on dc_d.id=pc_dc.productdiscount_id
                    where 1=1
                    and p.id = %s
                    and coalesce(dc_d.started, date('1900-01-01')) <= %s
                    and coalesce(dc_d.ended, date('2100-01-01')) > %s
                )q
                where p.id=q.id
                returning q.eff_id
            ''', [instance.id, timezone.now(), timezone.now()])
            rc = cr.rowcount
            output = cr.fetchone()
            # print("*** rowcount: %s, eff_id: %s" % (rc, output))
