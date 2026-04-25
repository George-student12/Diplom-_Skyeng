import allure
from Page.ui_page import MainPage
from conftest import driver


@allure.feature("Поиск")
@allure.story("Поиск товаров")
@allure.title("Поиск существующего товара")
@allure.severity(allure.severity_level.NORMAL)
def test_search_products(driver):
    main_page = MainPage(driver)
    main_page.open()
    results_page = main_page.search("Мастер и Маргарита")
    results_page.wait_for_results()
    assert results_page.has_products(), "Товары не найдены"


@allure.feature("Поиск")
@allure.story("Поиск товаров")
@allure.title("Поиск несуществующего товара")
@allure.severity(allure.severity_level.NORMAL)
def test_search_no_results(driver):
    main_page = MainPage(driver)
    main_page.open()
    results_page = main_page.search("xgkghkghkфывапролджэячсмитьбю")
    results_page.wait_for_results()
    assert results_page.is_empty_result(), "Ожидалась пустая выдача"


@allure.feature("Корзина")
@allure.story("Добавление товара")
@allure.title("Добавление товара в корзину со страницы поиска")
@allure.severity(allure.severity_level.CRITICAL)
def test_add_to_cart(driver):
    main_page = MainPage(driver)
    main_page.open()
    results_page = main_page.search("Мастер и Маргарита")
    results_page.wait_for_results()

    results_page.add_first_product_to_cart()
    cart_page = results_page.open_cart()
    cart_page.is_loaded()

    assert cart_page.has_items(), "В корзине нет товаров"


@allure.feature("Корзина")
@allure.story("Удаление товара")
@allure.title("Удаление товара из корзины")
@allure.severity(allure.severity_level.CRITICAL)
def test_remove_from_cart(driver):
    main_page = MainPage(driver)
    main_page.open()

    results_page = main_page.search("Мастер и Маргарита")
    results_page.wait_for_results()
    results_page.add_first_product_to_cart()

    cart_page = results_page.open_cart()
    cart_page.is_loaded()
    assert cart_page.has_items(), "Товар не добавился в корзину перед удалением"

    cart_page.remove_first_item()
    assert cart_page.is_empty(), "Корзина не пуста после удаления товара"


@allure.feature("Каталог")
@allure.story("Навигация по категориям")
@allure.title("Переход в подкатегорию 'Как стать успешным'")
@allure.severity(allure.severity_level.NORMAL)
def test_catalog_navigation(driver):
    main_page = MainPage(driver)
    main_page.open()
    main_page.open_catalog()
    main_page.select_category("Психология")
    catalog_page = main_page.select_subcategory(
        "psihologiya-uspekha-lichnaya-ehffektivnost-motivaciya-110337"
    )
    catalog_page.is_loaded()
    assert catalog_page.has_products(), "В каталоге нет товаров"
