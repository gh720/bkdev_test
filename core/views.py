import decimal

from django.http import JsonResponse
from django.views.generic import ListView

from core.models import Product


def get_decimal(s, *args):
    result = None
    if args:
        try:
            if s is not None:
                return decimal.Decimal(s)
        except decimal.DecimalException:
            pass
        return decimal.Decimal(args[0])
    return decimal.Decimal(s)


class price_list_c(ListView):
    def get_queryset(self):
        return super().get_queryset()

    def get(self, request, *args, **kwargs):
        order = request.GET.get('order', None)
        lower = get_decimal(request.GET.get('lower'), 100)
        upper = get_decimal(request.GET.get('upper'), min(lower, 10000))

        result=[]

        # disc = Product.objects.discounted_on_the_fly()
        # result = list(disc.values())

        disc = Product.objects.discounted().filter(eff_price__gte=lower, eff_price__lte=upper)
        if order is not None and order in ['eff_price']:
            disc = disc.order_by(order)

        result += list(disc.values())
        return JsonResponse(result, safe=False)

