import pytest
from django.urls import reverse
from rest_framework.status import HTTP_200_OK


@pytest.mark.django_db
def test_product_detail(api_client, product_factory):
    product = product_factory(name='test_product')
    url = reverse('products-detail', args=(product.id,))
    resp = api_client.get(url)
    resp_json = resp.json()
    assert resp.status_code == HTTP_200_OK
    assert resp_json['id'] == product.id
