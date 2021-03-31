from datetime import datetime

import pytest
from django.conf import settings
from django.contrib.auth.models import User
from django.urls import reverse
from model_bakery.random_gen import gen_decimal
from pytz import timezone
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_201_CREATED, \
    HTTP_403_FORBIDDEN, HTTP_204_NO_CONTENT, HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_order_retrieve(api_client, order_factory):
    """проверяем вывод конкретного заказа, пользователю только своего, админу любого, неавторизованному никакого"""
    test_user = User.objects.create_user('test_user', is_staff=False)
    test_admin = User.objects.create_user('test_admin', is_staff=True)
    user_order = order_factory(user=test_user)
    admin_order = order_factory(user=test_admin)
    user_url = reverse('orders-detail', args=(user_order.id,))
    admin_url = reverse('orders-detail', args=(admin_order.id,))
    resp_unauthorized_user_order = api_client.get(user_url)
    resp_unauthorized_admin_order = api_client.get(admin_url)
    api_client.force_authenticate(user=test_user)
    resp_user_user_order = api_client.get(user_url)
    resp_user_admin_order = api_client.get(admin_url)
    api_client.force_authenticate(user=test_admin)
    resp_admin_user_order = api_client.get(user_url)
    resp_admin_admin_order = api_client.get(admin_url)
    api_client.force_authenticate(user=None)
    assert resp_unauthorized_user_order.status_code == HTTP_401_UNAUTHORIZED
    assert resp_unauthorized_admin_order.status_code == HTTP_401_UNAUTHORIZED
    assert resp_user_user_order.status_code == HTTP_200_OK
    assert resp_user_admin_order.status_code == HTTP_403_FORBIDDEN
    assert resp_admin_user_order.status_code == HTTP_200_OK
    assert resp_admin_admin_order.status_code == HTTP_200_OK


@pytest.mark.django_db
def test_order_list(api_client, order_factory):
    """проверяем вывод списка заказов, пользователю только своего, админу всего, неавторизованному никакого"""
    test_user = User.objects.create_user('test_user', is_staff=False)
    test_admin = User.objects.create_user('test_admin', is_staff=True)
    order_factory(user=test_user)
    order_factory(user=test_admin)
    url = reverse('orders-list')
    resp_unauthorized_list = api_client.get(url)
    api_client.force_authenticate(user=test_user)
    resp_user_list = api_client.get(url)
    api_client.force_authenticate(user=test_admin)
    resp_admin_list = api_client.get(url)
    api_client.force_authenticate(user=None)
    assert resp_unauthorized_list.status_code == HTTP_401_UNAUTHORIZED
    assert resp_user_list.status_code == HTTP_200_OK
    assert len(resp_user_list.data) == 1
    assert resp_admin_list.status_code == HTTP_200_OK
    assert len(resp_admin_list.data) == 2


@pytest.mark.django_db
def test_order_create(api_client, product_factory):
    """проверяем создание заказа неавторизованным пользователем"""
    url = reverse('orders-list')
    product = product_factory()
    quantity = 10
    payload = {
        "products": [
            {
                "product_id": product.id,
                "quantity": quantity
            }
        ]
    }
    resp = api_client.post(url, payload, format='json')
    assert resp.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.django_db
def test_order_create_auth(api_client, product_factory):
    """проверяем создание заказа авторизованным пользователем и сумму заказа"""
    test_user = User.objects.create_user('test_user')
    url = reverse('orders-list')
    product_1 = product_factory()
    quantity_1 = 10
    product_2 = product_factory()
    quantity_2 = 10
    payload = {
        "products": [
            {
                "product_id": product_1.id,
                "quantity": quantity_1
            },
            {
                "product_id": product_2.id,
                "quantity": quantity_2
            }
        ]
    }
    api_client.force_authenticate(user=test_user)
    resp = api_client.post(url, payload, format='json')
    api_client.force_authenticate(user=None)
    resp_json = resp.json()
    assert resp.status_code == HTTP_201_CREATED
    total_amount = product_1.price * quantity_1 + product_2.price * quantity_2
    assert float(total_amount) == float(resp_json['total_amount'])


@pytest.mark.django_db
def test_order_update(api_client, product_factory, order_factory):
    """проверяем изменение заказа неавторизованным пользователем"""
    order = order_factory()
    url = reverse('orders-detail', args=(order.id,))
    product = product_factory()
    quantity = 10
    payload = {
        "products": [
            {
                "product_id": product.id,
                "quantity": quantity
            }
        ]
    }
    resp = api_client.put(url, payload, format='json')
    assert resp.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ['user_kwargs', 'expected_status'],
    (
            ({'is_staff': True}, HTTP_200_OK),
            ({'is_staff': False}, HTTP_400_BAD_REQUEST)
    )
)
@pytest.mark.django_db
def test_order_update_auth(api_client, product_factory, user_kwargs, expected_status):
    """проверяем изменение заказа авторизованным пользователем и изменение статуса админом"""
    test_user = User.objects.create_user('test_user', **user_kwargs)
    url = reverse('orders-list')
    product = product_factory()
    quantity = 10
    payload = {
        "products": [
            {
                "product_id": product.id,
                "quantity": quantity
            }
        ]
    }
    api_client.force_authenticate(user=test_user)
    resp = api_client.post(url, payload, format='json')
    resp_json = resp.json()

    new_quantity = 20
    url_update = reverse('orders-detail', args=(resp_json['id'],))
    payload_update = {
        "products": [
            {
                "product_id": product.id,
                "quantity": new_quantity
            }
        ],
        "status": "DONE"
    }
    resp_update = api_client.put(url_update, payload_update, format='json')
    resp_update_json = resp_update.json()
    api_client.force_authenticate(user=None)
    assert resp_update.status_code == expected_status
    if resp_update.status_code == 200:
        assert resp_update_json['status'] == 'DONE'
        new_total_amount = product.price * new_quantity
        assert float(new_total_amount) == float(resp_update_json['total_amount'])


@pytest.mark.django_db
def test_order_update_admin(api_client, product_factory):
    """проверяем что при изменение заказа пользователя админом не изменяется поле user"""
    test_user = User.objects.create_user('test_user', is_staff=False)
    test_admin = User.objects.create_user('test_admin', is_staff=True)
    url = reverse('orders-list')
    product = product_factory()
    quantity = 10
    payload = {
        "products": [
            {
                "product_id": product.id,
                "quantity": quantity
            }
        ]
    }
    api_client.force_authenticate(user=test_user)
    resp = api_client.post(url, payload, format='json')
    resp_json = resp.json()

    new_quantity = 20
    url_update = reverse('orders-detail', args=(resp_json['id'],))
    payload_update = {
        "products": [
            {
                "product_id": product.id,
                "quantity": new_quantity
            }
        ],
        "status": "DONE"
    }
    api_client.force_authenticate(user=test_admin)
    resp_update = api_client.put(url_update, payload_update, format='json')
    resp_update_json = resp_update.json()
    api_client.force_authenticate(user=None)
    assert resp_update.status_code == HTTP_200_OK
    assert resp_update_json['user']['id'] == test_user.id


@pytest.mark.django_db
def test_order_delete(api_client, order_factory):
    """проверяем невозможность удаления заказа неавторизованным пользователем"""
    order = order_factory()
    url = reverse('orders-detail', args=(order.id,))
    resp = api_client.delete(url, format='json')
    assert resp.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ['user_kwargs', 'expected_status'],
    (
            ({'is_staff': False}, HTTP_403_FORBIDDEN),
            ({'is_staff': True}, HTTP_204_NO_CONTENT)
    )
)
@pytest.mark.django_db
def test_order_delete_admin(api_client, order_factory, user_kwargs, expected_status):
    """проверяем удаление заказа админом и невозможность сторонним пользователем"""
    order_user = User.objects.create_user('order_user')
    order = order_factory(user=order_user)
    url = reverse('orders-detail', args=(order.id,))
    test_user = User.objects.create_user('test_user', **user_kwargs)
    api_client.force_authenticate(user=test_user)
    resp = api_client.delete(url, format='json')
    api_client.force_authenticate(user=None)
    assert resp.status_code == expected_status


@pytest.mark.django_db
def test_order_delete_auth(api_client, order_factory):
    """проверяем удаление заказа пользователем-создателем"""
    order_user = User.objects.create_user('order_user')
    order = order_factory(user=order_user)
    url = reverse('orders-detail', args=(order.id,))
    api_client.force_authenticate(user=order_user)
    resp = api_client.delete(url, format='json')
    api_client.force_authenticate(user=None)
    assert resp.status_code == HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_order_filter_status(api_client, order_factory):
    """проверяем фильтрацию по статуса"""
    done_qty = 7
    in_progress_qty = 2
    test_admin = User.objects.create_user('test_admin', is_staff=True)
    order_factory(_quantity=done_qty, status='DONE')
    order_factory(_quantity=in_progress_qty, status='IN_PROGRESS')
    url = reverse('orders-list')
    api_client.force_authenticate(user=test_admin)
    resp_done = api_client.get(url, {'status__iexact': 'DONE'})
    resp_in_progress = api_client.get(url, {'status__iexact': 'IN_PROGRESS'})
    api_client.force_authenticate(user=None)
    assert resp_done.status_code == HTTP_200_OK
    assert len(resp_done.json()) == done_qty
    assert resp_in_progress.status_code == HTTP_200_OK
    assert len(resp_in_progress.json()) == in_progress_qty


@pytest.mark.parametrize(
    ['filter_str', 'expression'],
    (
            ('total_amount', 'amount == filter_amount'),
            ('total_amount__lt', 'amount < filter_amount'),
            ('total_amount__lte', 'amount <= filter_amount'),
            ('total_amount__gt', 'amount > filter_amount'),
            ('total_amount__gte', 'amount >= filter_amount'),
    )
)
@pytest.mark.django_db
def test_order_filter_total_amount(api_client, order_factory, filter_str, expression):
    """проверяем фильтр по общей сумме"""
    order_amounts = []
    for _ in range(5):
        order = order_factory(total_amount=gen_decimal(max_digits=8, decimal_places=2))
        order_amounts.append(float(order.total_amount))
    filter_amount = order_amounts[2]
    test_admin = User.objects.create_user('test_user', is_staff=True)
    url = reverse('orders-list')
    api_client.force_authenticate(user=test_admin)
    resp = api_client.get(url, {filter_str: filter_amount})
    api_client.force_authenticate(user=None)
    resp_json = resp.json()
    amount_list = [float(_['total_amount']) for _ in resp_json]
    assert resp.status_code == HTTP_200_OK
    for amount in order_amounts:
        if eval(expression):
            assert amount in amount_list
        else:
            assert amount not in amount_list


@pytest.mark.parametrize(
    ['filter_str', 'dict_key'],
    (
            ('created_at__date', 'created_at'),
            ('updated_at__date', 'updated_at'),
    )
)
@pytest.mark.django_db
def test_order_filter_created_updated(api_client, order_factory, filter_str, dict_key):
    """проверяем фильтрацию списка заказов по дате создания и обновления"""
    orders = order_factory(_quantity=5)
    url = reverse('orders-list')
    orders_dates = [_.created_at for _ in orders]
    filter_order_date = datetime.date(orders_dates[2].astimezone(timezone(settings.TIME_ZONE)))
    test_admin = User.objects.create_user('test_user', is_staff=True)
    api_client.force_authenticate(user=test_admin)
    resp = api_client.get(url, {filter_str: filter_order_date})
    api_client.force_authenticate(user=None)
    resp_json = resp.json()
    resp_dates_set = {datetime.strptime(_[dict_key], "%Y-%m-%dT%H:%M:%S.%f%z").date() for _ in resp_json}
    assert resp.status_code == HTTP_200_OK
    assert {filter_order_date} == resp_dates_set


@pytest.mark.parametrize(
    ['filter_str', 'dict_key'],
    (
            ('created_at__date_gte', 'created_at'),
            ('updated_at__date_gte', 'updated_at'),
    )
)
@pytest.mark.django_db
def test_order_filter_created_updated_gte(api_client, order_factory, filter_str, dict_key):
    """проверяем фильтрацию списка заказов по дате создания и обновления больше или равно"""
    orders = order_factory(_quantity=5)
    url = reverse('orders-list')
    orders_dates = [_.created_at for _ in orders]
    filter_order_date = datetime.date(orders_dates[2].astimezone(timezone(settings.TIME_ZONE)))
    test_admin = User.objects.create_user('test_user', is_staff=True)
    api_client.force_authenticate(user=test_admin)
    resp = api_client.get(url, {filter_str: filter_order_date})
    api_client.force_authenticate(user=None)
    resp_json = resp.json()
    resp_dates_list = [datetime.strptime(_[dict_key], "%Y-%m-%dT%H:%M:%S.%f%z").date() for _ in resp_json]
    assert resp.status_code == HTTP_200_OK
    assert all(date >= filter_order_date for date in resp_dates_list)


@pytest.mark.parametrize(
    ['filter_str', 'dict_key'],
    (
            ('created_at__date_lte', 'created_at'),
            ('updated_at__date_lte', 'updated_at'),
    )
)
@pytest.mark.django_db
def test_order_filter_created_updated_lte(api_client, order_factory, filter_str, dict_key):
    """проверяем фильтрацию списка заказов по дате создания и обновления меньше или равно"""
    orders = order_factory(_quantity=5)
    url = reverse('orders-list')
    orders_dates = [_.created_at for _ in orders]
    filter_order_date = datetime.date(orders_dates[2].astimezone(timezone(settings.TIME_ZONE)))
    test_admin = User.objects.create_user('test_user', is_staff=True)
    api_client.force_authenticate(user=test_admin)
    resp = api_client.get(url, {filter_str: filter_order_date})
    api_client.force_authenticate(user=None)
    resp_json = resp.json()
    resp_dates_list = [datetime.strptime(_[dict_key], "%Y-%m-%dT%H:%M:%S.%f%z").date() for _ in resp_json]
    assert resp.status_code == HTTP_200_OK
    assert all(date <= filter_order_date for date in resp_dates_list)


@pytest.mark.django_db
def test_order_filter_products(api_client, order_factory, product_factory):
    """проверяем фильтрацию списка заказов по продуктам"""
    products = product_factory(_quantity=5)
    product_ids = [_.id for _ in products]
    filter_product_id = product_ids[2]
    url_create = reverse('orders-list')
    test_admin = User.objects.create_user('test_user', is_staff=True)
    api_client.force_authenticate(user=test_admin)
    for product_id in product_ids:
        payload = {
            "products": [
                {
                    "product_id": product_id,
                    "quantity": 2
                }
            ]
        }
        api_client.post(url_create, payload, format='json')

    url = reverse('orders-list')
    resp = api_client.get(url, {'products__id': filter_product_id})
    api_client.force_authenticate(user=None)
    resp_json = resp.json()
    assert resp.status_code == HTTP_200_OK
    filtered_products_list = [_['products'] for _ in resp_json]
    for filtered_products in filtered_products_list:
        assert filter_product_id in [_['product_id'] for _ in filtered_products]
