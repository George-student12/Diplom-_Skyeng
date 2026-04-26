import allure
import pytest
import requests
from conftest import BASE_URL, HEADERS


@pytest.mark.regression
@pytest.mark.cart
@pytest.mark.api
@allure.feature("Корзина API")
@allure.story("Добавление товара")
@allure.title("Добавление товара в корзину через API")
@allure.severity(allure.severity_level.CRITICAL)
def test_add_to_cart():
    url = f"{BASE_URL}/v1/cart/product"
    payload = {"id": 3018590}

    with allure.step(f"POST {url} с товаром {payload['id']}"):
        response = requests.post(url, headers=HEADERS, json=payload)

    with allure.step("Проверить статус код 200"):
        assert response.status_code == 200


@pytest.mark.regression
@pytest.mark.cart
@pytest.mark.api
@allure.feature("Корзина API")
@allure.story("Изменение количества")
@allure.title("Изменение количества товара в корзине")
@allure.severity(allure.severity_level.NORMAL)
def test_changes_quantity():
    url = f"{BASE_URL}/v1/cart/product"
    payload = {
        "id": 3018590
    }

    with allure.step(f"POST {url} с товаром {payload['id']}"):
        response = requests.post(url, headers=HEADERS, json=payload)

        assert response.status_code == 200

    url = f"{BASE_URL}/v1/cart"
    payload = {
        "id": 259333072,
        "quantity": 10
    }

    with allure.step(f"PUT {url} с quantity={payload['quantity']}"):
        response = requests.put(url, headers=HEADERS, json=payload)

    with allure.step("Проверить статус код 200"):
        assert response.status_code == 200


@pytest.mark.regression
@pytest.mark.cart
@pytest.mark.api
@allure.feature("Корзина API")
@allure.story("Получение информации о корзине")
@allure.title("Получение краткой информации о корзине")
@allure.severity(allure.severity_level.NORMAL)
def test_search_products_api():
    url = f"{BASE_URL}/v1/cart/short"
    payload = {
        "data": {
            "items": [3018590],
            "quantity": 1
        }
    }

    with allure.step(f"GET {url}"):
        response = requests.get(url, headers=HEADERS, json=payload)

    with allure.step("Проверить статус код 200"):
        assert response.status_code == 200


@pytest.mark.regression
@pytest.mark.cart
@pytest.mark.api
@allure.feature("Корзина API")
@allure.story("Обработка ошибок")
@allure.title("Некорректный метод POST (ожидается 405)")
@allure.severity(allure.severity_level.MINOR)
def test_failed_status_code():
    url = f"{BASE_URL}/v1/cart"
    payload = {"id": 3018590}

    with allure.step(f"POST {url} (неподдерживаемый метод)"):
        response = requests.post(url, headers=HEADERS, json=payload)

    with allure.step("Проверить статус код 405"):
        assert response.status_code == 405


@pytest.mark.regression
@pytest.mark.cart
@pytest.mark.api
@allure.feature("Корзина API")
@allure.story("Обработка ошибок")
@allure.title("Запрос несуществующей версии v3 (ожидается 404)")
@allure.severity(allure.severity_level.MINOR)
def test_failed_city_id():
    url = f"{BASE_URL}/v3/cart/product"
    payload = {"id": 3138357}

    with allure.step(f"GET {url} с несуществующим id"):
        response = requests.get(url, headers=HEADERS, json=payload)

    with allure.step("Проверить статус код 404"):
        assert response.status_code == 404
