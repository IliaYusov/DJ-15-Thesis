import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from model_bakery.random_gen import gen_text
from products.models import Product
from rest_framework.status import HTTP_200_OK, HTTP_201_CREATED, HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN, \
    HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_product_retrieve(api_client, product_factory):
    """проверяем вывод конкретного продукта"""
    product = product_factory(name='test_product')
    url = reverse('products-detail', args=(product.id,))
    resp = api_client.get(url)
    resp_json = resp.json()
    assert resp.status_code == HTTP_200_OK
    assert resp_json['id'] == product.id


@pytest.mark.django_db
def test_product_list(api_client, product_factory):
    """проверяем вывод списка продуктов"""
    products = product_factory(_quantity=5)
    url = reverse('products-list')
    resp = api_client.get(url)
    resp_json = resp.json()
    products_ids = {_.id for _ in products}
    resp_ids = {_['id'] for _ in resp_json}
    assert resp.status_code == HTTP_200_OK
    assert products_ids == resp_ids


@pytest.mark.django_db
def test_product_create(api_client):
    """проверяем невозможность создания продукта неавторизованным пользователем"""
    url = reverse('products-list')
    product_name = 'test_product4583408'
    product_description = 'foo bar'
    product_price = '100.00'
    payload = {
        'name': product_name,
        'description': product_description,
        'price': product_price
    }
    resp = api_client.post(url, payload, format='json')
    assert resp.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ['user_kwargs', 'expected_status'],
    (
            ({'is_staff': True}, HTTP_201_CREATED),
            ({'is_staff': False}, HTTP_403_FORBIDDEN)
    )
)
@pytest.mark.django_db
def test_product_create_auth(api_client, user_kwargs, expected_status):
    """проверяем создание продукта админом и невозможность создания пользователем"""
    url = reverse('products-list')
    product_name = 'test_product4583408'
    product_description = 'foo bar'
    product_price = 100.00
    payload = {
        'name': product_name,
        'description': product_description,
        'price': product_price
    }
    test_user = User.objects.create_user('test_user', **user_kwargs)
    api_client.force_authenticate(user=test_user)
    resp = api_client.post(url, payload, format='json')
    api_client.force_authenticate(user=None)
    resp_json = resp.json()
    assert resp.status_code == expected_status
    if resp.status_code == 201:
        new_product = Product.objects.get(id=resp_json['id'])
        assert new_product.name == product_name
        assert new_product.description == product_description
        assert new_product.price == product_price


@pytest.mark.django_db
def test_product_update(api_client, product_factory):
    """проверяем невозможность изменения продукта неавторизованным пользователем"""
    products = product_factory(_quantity=5)
    product_ids = [_.id for _ in products]
    product_id_to_update = product_ids[2]
    url = reverse('products-detail', args=(product_id_to_update,))
    product_name = 'test_product4583408'
    product_description = 'foo bar'
    product_price = '100.00'
    payload = {
        'name': product_name,
        'description': product_description,
        'price': product_price
    }
    resp = api_client.put(url, payload, format='json')
    assert resp.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ['user_kwargs', 'expected_status'],
    (
            ({'is_staff': True}, HTTP_200_OK),
            ({'is_staff': False}, HTTP_403_FORBIDDEN)
    )
)
@pytest.mark.django_db
def test_product_update_auth(api_client, product_factory, user_kwargs, expected_status):
    """проверяем изменение продукта админом и невозможность изменения пользователем"""
    products = product_factory(_quantity=5)
    product_ids = [_.id for _ in products]
    product_id_to_update = product_ids[2]
    url = reverse('products-detail', args=(product_id_to_update,))
    product_name = 'test_product4583408'
    product_description = 'foo bar'
    product_price = 100.00
    payload = {
        'name': product_name,
        'description': product_description,
        'price': product_price
    }
    test_user = User.objects.create_user('test_user', **user_kwargs)
    api_client.force_authenticate(user=test_user)
    resp = api_client.put(url, payload, format='json')
    api_client.force_authenticate(user=None)
    assert resp.status_code == expected_status
    if resp.status_code == 200:
        updated_product = Product.objects.get(id=product_id_to_update)
        assert updated_product.name == product_name
        assert updated_product.description == product_description
        assert updated_product.price == product_price


@pytest.mark.django_db
def test_product_delete(api_client, product_factory):
    """проверяем невозможность удаления продукта неавторизованным пользователем"""
    products = product_factory(_quantity=5)
    product_ids = [_.id for _ in products]
    product_id_to_delete = product_ids[2]
    url = reverse('products-detail', args=(product_id_to_delete,))
    resp = api_client.delete(url, format='json')
    assert resp.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ['user_kwargs', 'expected_status'],
    (
            ({'is_staff': True}, HTTP_204_NO_CONTENT),
            ({'is_staff': False}, HTTP_403_FORBIDDEN)
    )
)
@pytest.mark.django_db
def test_product_delete_auth(api_client, product_factory, user_kwargs, expected_status):
    """проверяем удаление продукта админом и невозможность удаления пользователем"""
    products = product_factory(_quantity=5)
    product_ids = [_.id for _ in products]
    product_id_to_delete = product_ids[2]
    url = reverse('products-detail', args=(product_id_to_delete,))
    test_user = User.objects.create_user('test_user', **user_kwargs)
    api_client.force_authenticate(user=test_user)
    resp = api_client.delete(url, format='json')
    api_client.force_authenticate(user=None)
    assert resp.status_code == expected_status


@pytest.mark.django_db
def test_product_list_filter_name(api_client, product_factory):
    """проверяем фильтрацию списка продуктов по имени"""
    products = product_factory(_quantity=5)
    url = reverse('products-list')
    product_names = [_.name for _ in products]
    filter_name = product_names[2]
    resp1 = api_client.get(url, {'name__iexact': filter_name})
    resp2 = api_client.get(url, {'name__icontains': filter_name[1:-1]})
    resp1_json = resp1.json()
    resp2_json = resp2.json()
    resp1_names = {_['name'] for _ in resp1_json}
    resp2_names = {_['name'] for _ in resp2_json}
    assert resp1.status_code == HTTP_200_OK
    assert resp2.status_code == HTTP_200_OK
    assert {filter_name} == resp1_names == resp2_names


@pytest.mark.django_db
def test_product_list_filter_description(api_client, product_factory):
    """проверяем фильтрацию списка продуктов по описанию"""
    products = product_factory(_quantity=5, description=gen_text)
    url = reverse('products-list')
    product_desc = [_.description for _ in products]
    filter_desc = product_desc[2]
    resp = api_client.get(url, {'description__icontains': filter_desc[1:-1]})
    resp_json = resp.json()
    resp_desc = {_['description'] for _ in resp_json}
    assert resp.status_code == HTTP_200_OK
    assert {filter_desc} == resp_desc


@pytest.mark.django_db
def test_product_list_filter_price_exact(api_client, product_factory):
    """проверяем фильтрацию списка продуктов по цене точно"""
    products = product_factory(_quantity=5)
    url = reverse('products-list')
    product_prices = [_.price for _ in products]
    filter_price = product_prices[2]
    resp = api_client.get(url, {'price': filter_price})
    resp_json = resp.json()
    resp_price = {_['price'] for _ in resp_json}
    assert resp.status_code == HTTP_200_OK
    assert {str(filter_price)} == resp_price


@pytest.mark.django_db
def test_product_list_filter_price_lte(api_client, product_factory):
    """проверяем фильтрацию списка продуктов по цене меньше или равно"""
    products = product_factory(_quantity=5)
    url = reverse('products-list')
    product_prices = [_.price for _ in products]
    product_prices.sort()
    filter_price = product_prices[2]
    resp = api_client.get(url, {'price__lte': filter_price})
    resp_json = resp.json()
    resp_prices = {_['price'] for _ in resp_json}
    assert resp.status_code == HTTP_200_OK
    assert all(float(price) <= float(filter_price) for price in resp_prices)


@pytest.mark.django_db
def test_product_list_filter_price_gte(api_client, product_factory):
    """проверяем фильтрацию списка продуктов по цене больше или равно"""
    products = product_factory(_quantity=5)
    url = reverse('products-list')
    product_prices = [_.price for _ in products]
    product_prices.sort()
    filter_price = product_prices[2]
    resp = api_client.get(url, {'price__gte': filter_price})
    resp_json = resp.json()
    resp_prices = {_['price'] for _ in resp_json}
    assert resp.status_code == HTTP_200_OK
    assert all(float(price) >= float(filter_price) for price in resp_prices)
