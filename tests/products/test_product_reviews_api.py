from datetime import datetime
from pytz import timezone

import pytest
from django.contrib.auth.models import User
from django.urls import reverse
from products.models import ProductReview
from django.conf import settings
from rest_framework.status import HTTP_200_OK, HTTP_401_UNAUTHORIZED, HTTP_201_CREATED, HTTP_403_FORBIDDEN, \
    HTTP_400_BAD_REQUEST, HTTP_204_NO_CONTENT


@pytest.mark.django_db
def test_product_review_retrieve(api_client, product_review_factory):
    """проверяем вывод конкретного отзыва"""
    product_review = product_review_factory()
    url = reverse('product-reviews-detail', args=(product_review.id,))
    resp = api_client.get(url)
    resp_json = resp.json()
    assert resp.status_code == HTTP_200_OK
    assert resp_json['id'] == product_review.id


@pytest.mark.django_db
def test_product_review_list(api_client, product_review_factory):
    """проверяем вывод списка отзывов"""
    product_reviews = product_review_factory(_quantity=5)
    url = reverse('product-reviews-list')
    resp = api_client.get(url)
    resp_json = resp.json()
    review_ids = {_.id for _ in product_reviews}
    resp_ids = {_['id'] for _ in resp_json}
    assert resp.status_code == HTTP_200_OK
    assert review_ids == resp_ids


@pytest.mark.django_db
def test_product_review_create(api_client, product_factory):
    """проверяем невозможность создания отзыва не авторизованным пользователем"""
    url = reverse('product-reviews-list')
    product = product_factory()
    review_product_id = product.id
    review_text = 'foo bar'
    review_rating = 5
    payload = {
        'product_id': review_product_id,
        'text': review_text,
        'rating': review_rating
    }
    resp = api_client.post(url, payload, format='json')
    assert resp.status_code == HTTP_401_UNAUTHORIZED


@pytest.mark.parametrize(
    ['text', 'rating', 'expected_status'],
    (
            ('foo_bar', 5, HTTP_201_CREATED),
            ('', 5, HTTP_201_CREATED),
            ('', 0, HTTP_400_BAD_REQUEST),
            ('', 6, HTTP_400_BAD_REQUEST)
    )
)
@pytest.mark.django_db
def test_product_review_create_auth(api_client, product_factory, expected_status, text, rating):
    """проверяем создание отзыва и невозможность создания повторного отзыва"""
    url = reverse('product-reviews-list')
    product = product_factory()
    review_product_id = product.id
    review_text = text
    review_rating = rating
    payload = {
        'product_id': review_product_id,
        'text': review_text,
        'rating': review_rating
    }
    test_user = User.objects.create_user('test_user')
    api_client.force_authenticate(user=test_user)
    resp = api_client.post(url, payload, format='json')
    resp2 = api_client.post(url, payload, format='json')
    api_client.force_authenticate(user=None)
    assert resp.status_code == expected_status
    assert resp2.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_product_review_update(api_client, product_factory):
    """проверяем изменение отзыва автором и невозможность изменения другим пользователем"""
    url_create = reverse('product-reviews-list')
    product = product_factory(name='test_product')
    review_product_id = product.id
    review_text = 'foo bar'
    review_rating = 2
    payload_create = {
        'product_id': review_product_id,
        'text': review_text,
        'rating': review_rating
    }
    test_user_owner = User.objects.create_user('test_user_owner')
    test_user_not_owner = User.objects.create_user('test_user_not_owner')
    api_client.force_authenticate(user=test_user_owner)
    create_resp = api_client.post(url_create, payload_create, format='json')
    create_resp_json = create_resp.json()

    url_update = reverse('product-reviews-detail', args=(create_resp_json['id'],))
    new_review_rating = 5
    payload = {
        'product_id': review_product_id,
        'rating': new_review_rating
    }
    resp_owner = api_client.put(url_update, payload, format='json')
    api_client.force_authenticate(user=test_user_not_owner)
    resp_not_owner = api_client.put(url_update, payload, format='json')
    api_client.force_authenticate(user=None)
    assert resp_owner.status_code == HTTP_200_OK
    assert resp_not_owner.status_code == HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_product_review_update_auth(api_client, product_factory):
    """проверяем изменение отзыва автором и невозможность второго отзыва на тот же продукт"""
    url_create = reverse('product-reviews-list')
    product_1 = product_factory()
    product_2 = product_factory()
    review_product_1_id = product_1.id
    review_product_2_id = product_2.id
    review_text = 'foo bar'
    review_rating = 2
    payload_create_1 = {
        'product_id': review_product_1_id,
        'text': review_text,
        'rating': review_rating
    }
    payload_create_2 = {
        'product_id': review_product_2_id,
        'text': review_text,
        'rating': review_rating
    }
    test_user = User.objects.create_user('test_user')
    api_client.force_authenticate(user=test_user)
    create_resp = api_client.post(url_create, payload_create_1, format='json')
    api_client.post(url_create, payload_create_2, format='json')
    create_resp_json = create_resp.json()

    url_update = reverse('product-reviews-detail', args=(create_resp_json['id'],))
    new_review_rating = 5
    payload_1 = {
        'product_id': review_product_1_id,
        'rating': new_review_rating
    }
    resp_1 = api_client.put(url_update, payload_1, format='json')
    payload_2 = {
        'product_id': review_product_2_id,
        'rating': new_review_rating
    }
    resp_2 = api_client.put(url_update, payload_2, format='json')
    api_client.force_authenticate(user=None)
    assert resp_1.status_code == HTTP_200_OK
    assert resp_2.status_code == HTTP_400_BAD_REQUEST


@pytest.mark.django_db
def test_product_review_destroy(api_client, product_factory):
    """проверяем удаление отзыва автором и невозможность удаления другим пользователем"""
    url_create = reverse('product-reviews-list')
    product = product_factory()
    review_product_id = product.id
    review_text = 'foo bar'
    review_rating = 5
    payload_create = {
        'product_id': review_product_id,
        'text': review_text,
        'rating': review_rating
    }
    test_user_owner = User.objects.create_user('test_user_owner')
    test_user_not_owner = User.objects.create_user('test_user_not_owner')
    api_client.force_authenticate(user=test_user_owner)
    create_owner_resp = api_client.post(url_create, payload_create, format='json')
    create_resp_json = create_owner_resp.json()

    url_destroy = reverse('product-reviews-detail', args=(create_resp_json['id'],))
    api_client.force_authenticate(user=test_user_not_owner)
    resp_not_owner = api_client.delete(url_destroy, format='json')
    api_client.force_authenticate(user=test_user_owner)
    resp_owner = api_client.delete(url_destroy, format='json')
    api_client.force_authenticate(user=None)
    assert resp_owner.status_code == HTTP_204_NO_CONTENT
    assert resp_not_owner.status_code == HTTP_403_FORBIDDEN


@pytest.mark.django_db
def test_product_review_filter_user_id(api_client, product_review_factory):
    """проверяем фильтрацию списка отзывов по id пользователя"""
    product_reviews = product_review_factory(_quantity=5)
    url = reverse('product-reviews-list')
    product_reviews_users = [_.user for _ in product_reviews]
    filter_user_id = product_reviews_users[2].id
    resp = api_client.get(url, {'user': filter_user_id})
    resp_json = resp.json()
    resp_user_ids = {_['user']['id'] for _ in resp_json}
    assert resp.status_code == HTTP_200_OK
    assert {filter_user_id} == resp_user_ids


@pytest.mark.django_db
def test_product_review_filter_product_id(api_client, product_review_factory):
    """проверяем фильтрацию списка отзывов по id товара"""
    product_reviews = product_review_factory(_quantity=5)
    url = reverse('product-reviews-list')
    product_reviews_products = [_.product for _ in product_reviews]
    filter_product_id = product_reviews_products[2].id
    resp = api_client.get(url, {'product': filter_product_id})
    resp_json = resp.json()
    resp_user_ids = {_['product']['id'] for _ in resp_json}
    assert resp.status_code == HTTP_200_OK
    assert {filter_product_id} == resp_user_ids


@pytest.mark.django_db
def test_product_review_filter_created_at(api_client, product_review_factory):
    """проверяем фильтрацию списка отзывов по дате создания точно"""
    product_reviews = product_review_factory(_quantity=5)
    url = reverse('product-reviews-list')
    product_reviews_dates = [_.created_at for _ in product_reviews]
    filter_product_date = datetime.date(product_reviews_dates[2].astimezone(timezone(settings.TIME_ZONE)))
    resp = api_client.get(url, {'created_at__date': filter_product_date})
    resp_json = resp.json()
    resp_dates_set = {datetime.strptime(_['created_at'], "%Y-%m-%dT%H:%M:%S.%f%z").date() for _ in resp_json}
    assert resp.status_code == HTTP_200_OK
    assert {filter_product_date} == resp_dates_set


@pytest.mark.django_db
def test_product_review_filter_created_at_gte(api_client, product_review_factory):
    """проверяем фильтрацию списка отзывов по дате создания больше или равно"""
    product_reviews = product_review_factory(_quantity=5)
    url = reverse('product-reviews-list')
    product_reviews_dates = [_.created_at for _ in product_reviews]
    filter_product_date = datetime.date(product_reviews_dates[2].astimezone(timezone(settings.TIME_ZONE)))
    resp = api_client.get(url, {'created_at__date__gte': filter_product_date})
    resp_json = resp.json()
    resp_dates_list = [datetime.strptime(_['created_at'], "%Y-%m-%dT%H:%M:%S.%f%z").date() for _ in resp_json]
    assert resp.status_code == HTTP_200_OK
    assert all(date >= filter_product_date for date in resp_dates_list)


@pytest.mark.django_db
def test_product_review_filter_created_at_lte(api_client, product_review_factory):
    """проверяем фильтрацию списка отзывов по дате создания меньше или равно"""
    product_reviews = product_review_factory(_quantity=5)
    url = reverse('product-reviews-list')
    product_reviews_dates = [_.created_at for _ in product_reviews]
    filter_product_date = datetime.date(product_reviews_dates[2].astimezone(timezone(settings.TIME_ZONE)))
    resp = api_client.get(url, {'created_at__date__lte': filter_product_date})
    resp_json = resp.json()
    resp_dates_list = [datetime.strptime(_['created_at'], "%Y-%m-%dT%H:%M:%S.%f%z").date() for _ in resp_json]
    assert resp.status_code == HTTP_200_OK
    assert all(date <= filter_product_date for date in resp_dates_list)
