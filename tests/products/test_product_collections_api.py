import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from products.models import ProductCollection
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_201_CREATED, \
    HTTP_403_FORBIDDEN, HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_product_collection_retrieve(api_client, product_collection_factory):
    """проверяем вывод конкретной подборки"""
    product_collection = product_collection_factory()
    url = reverse('product-collections-detail', args=(product_collection.id,))
    resp = api_client.get(url)
    resp_json = resp.json()
    assert resp.status_code == HTTP_200_OK
    assert resp_json['id'] == product_collection.id


@pytest.mark.django_db
def test_product_collection_list(api_client, product_collection_factory):
    """проверяем вывод списка подборок"""
    product_collections = product_collection_factory(_quantity=5)
    url = reverse('product-collections-list')
    resp = api_client.get(url)
    resp_json = resp.json()
    collections_ids = {_.id for _ in product_collections}
    resp_ids = {_['id'] for _ in resp_json}
    assert resp.status_code == HTTP_200_OK
    assert collections_ids == resp_ids


@pytest.mark.django_db
def test_product_collection_create(api_client, product_factory):
    """проверяем невозможность создания подборки неавторизованным пользователем"""
    url = reverse('product-collections-list')
    products = product_factory(_quantity=5)
    product_ids = [_.id for _ in products]
    name = 'foo bar'
    text = 'nice collection'
    payload = {
        'name': name,
        'text': text,
        'products': [{'product_id': _} for _ in product_ids]
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
def test_product_collection_create_auth(api_client, product_factory, user_kwargs, expected_status):
    """проверяем создание подборки админом и невозможность создания пользователем"""
    url = reverse('product-collections-list')
    products = product_factory(_quantity=5)
    product_ids = [_.id for _ in products]
    name = 'foo bar'
    text = 'nice collection'
    payload = {
        'name': name,
        'text': text,
        'products': [{'product_id': _} for _ in product_ids]
    }

    test_user = User.objects.create_user('test_user', **user_kwargs)
    api_client.force_authenticate(user=test_user)
    resp = api_client.post(url, payload, format='json')
    api_client.force_authenticate(user=None)
    resp_json = resp.json()
    assert resp.status_code == expected_status
    if resp.status_code == 201:
        new_collection = ProductCollection.objects.get(id=resp_json['id'])
        assert new_collection.name == name
        assert new_collection.text == text
        assert list(new_collection.products.all()) == products


@pytest.mark.django_db
def test_product_collection_update(api_client, product_collection_factory):
    """проверяем невозможность изменения подборки неавторизованным пользователем"""
    product_collection = product_collection_factory()
    url = reverse('product-collections-detail', args=(product_collection.id,))
    new_name = 'new_name'
    new_payload = {
        'name': new_name
    }
    resp = api_client.put(url, new_payload, format='json')
    assert resp.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ['user_kwargs', 'expected_status'],
    (
            ({'is_staff': True}, HTTP_200_OK),
            ({'is_staff': False}, HTTP_403_FORBIDDEN)
    )
)
@pytest.mark.django_db
def test_product_collection_update_auth(
        api_client,
        product_collection_factory,
        product_factory,
        user_kwargs,
        expected_status
):
    """проверяем изменение подборки админом и невозможность изменения пользователем"""
    product_collection = product_collection_factory()
    new_products = product_factory(_quantity=3)
    new_product_ids = [_.id for _ in new_products]
    url = reverse('product-collections-detail', args=(product_collection.id,))
    new_name = 'new_name'
    payload = {
        'name': new_name,
        'products': [{'product_id': _} for _ in new_product_ids]
    }
    test_user = User.objects.create_user('test_user', **user_kwargs)
    api_client.force_authenticate(user=test_user)
    resp = api_client.put(url, payload, format='json')
    api_client.force_authenticate(user=None)
    resp_json = resp.json()
    assert resp.status_code == expected_status
    if resp.status_code == 201:
        updated_collection = ProductCollection.objects.get(id=resp_json['id'])
        assert updated_collection.name == new_name
        assert list(updated_collection.products.all()) == new_products


@pytest.mark.django_db
def test_product_collection_delete(api_client, product_collection_factory):
    """проверяем невозможность удаления подборки неавторизованным пользователем"""
    collections = product_collection_factory(_quantity=5)
    collection_ids = [_.id for _ in collections]
    collection_id_to_delete = collection_ids[2]
    url = reverse('product-collections-detail', args=(collection_id_to_delete,))
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
def test_product_collection_delete_auth(
        api_client,
        product_collection_factory,
        user_kwargs,
        expected_status
):
    """проверяем удаление подборки админом и невозможность удаления пользователем"""
    collections = product_collection_factory(_quantity=5)
    collection_ids = [_.id for _ in collections]
    collection_id_to_delete = collection_ids[2]
    url = reverse('product-collections-detail', args=(collection_id_to_delete,))
    test_user = User.objects.create_user('test_user', **user_kwargs)
    api_client.force_authenticate(user=test_user)
    resp = api_client.delete(url, format='json')
    api_client.force_authenticate(user=None)
    assert resp.status_code == expected_status


@pytest.mark.django_db
def test_product_collection_list_name_filter(api_client, product_collection_factory):
    """проверяем фильтрацию списка подборок по имени"""
    collections = product_collection_factory(_quantity=5)
    url = reverse('product-collections-list')
    collection_names = [_.name for _ in collections]
    filter_name = collection_names[2]
    resp1 = api_client.get(url, {'name__iexact': filter_name})
    resp2 = api_client.get(url, {'name__icontains': filter_name[1:-1]})
    resp1_json = resp1.json()
    resp2_json = resp2.json()
    resp1_names = {_['name'] for _ in resp1_json}
    resp2_names = {_['name'] for _ in resp2_json}
    assert resp1.status_code == HTTP_200_OK
    assert resp2.status_code == HTTP_200_OK
    assert {filter_name} == resp1_names == resp2_names
