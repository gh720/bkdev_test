import json
import os
import sys
import pprint as pp
import django

from json import encoder

os.environ['DJANGO_SETTINGS_MODULE'] = 'punchbag.settings'
django.setup()

from core.views import price_list_c

from django.test import RequestFactory

### checking the view: ordering and filtering

request_factory = RequestFactory()
my_url = '/?order=eff_price&lower=100&upper=1000'
my_request = request_factory.get(my_url)

view = price_list_c.as_view()
response = view(my_request)
data = json.loads(response.content)

pp.pprint(data, indent=2, width=200)
