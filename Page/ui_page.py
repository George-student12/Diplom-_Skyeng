import allure
from selenium.common import TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.wait import WebDriverWait
from selenium.common import StaleElementReferenceException


class MainPage:
    """Главная страница интернет-магазина «Читай-город»."""

    def __init__(self, driver):
        self.driver = driver
        self.wait = WebDriverWait(driver, 10)

    @allure.step("Открыть главную страницу и принять куки")
    def open(self):
        self.driver.get("https://www.chitai-gorod.ru/")
        try:
            cookie_btn = self.wait.until(
                EC.
                element_to_be_clickable
                ((By.CSS_SELECTOR, ".cookie-notice__button"))
            )
            cookie_btn.click()
        except Exception:
            pass

        """ Закрываем окно выбора города, если оно появилось """
        try:
            (self.wait.until(EC.element_to_be_clickable((
                By.XPATH,
                "//div[@class='header-location-popup__controls']"
                " // div[text()='Да, я здесь ']"
            ))).click())
        except Exception:
            pass

        return self

    @allure.step("Выполнить поиск по запросу: '{query}'")
    def search(self, query: str):
        """Вводит поисковый запрос и отправляет форму."""
        search_input = self.wait.until(
            EC.presence_of_element_located((By.ID, "app-search"))
        )
        search_input.clear()
        search_input.send_keys(query)

        submit_button = self.wait.until(
            EC.
            element_to_be_clickable
            ((By.CSS_SELECTOR, "button.search-form__button-search"))
        )
        submit_button.click()

        return SearchResultsPage(self.driver, self.wait)

    @allure.step("Открыть каталог (кнопка 'Каталог')")
    def open_catalog(self):
        """Открывает боковое меню каталога."""
        catalog_btn = self.wait.until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button.catalog-btn"))
        )
        catalog_btn.click()
        return self

    @allure.step("Выбрать категорию: '{category_name}'")
    def select_category(self, category_name: str):
        """ Кликаем по категории
         (можно обычным кликом, но для надёжности - JavaScript) """
        category = self.wait.until(
            EC.
            presence_of_element_located
            ((By.XPATH, f"//span[contains(@class,"
                        f" 'categories-level-menu__item-title')"
                        f" and text()='{category_name}']"))
        )
        self.driver.execute_script("arguments[0].click();", category)

        """ Ждём, пока в DOM появится хотя бы одна подкатегория """
        self.wait.until(
            EC.
            presence_of_element_located
            ((By.CSS_SELECTOR, ".categories-level-menu__item"))
        )
        return self

    @allure.step("Выбрать подкатегорию по href: '{subcategory_href}'")
    def select_subcategory(self, subcategory_href: str):
        """ Убеждаемся, что элемент с нужным href присутствует в DOM """
        self.wait.until(
            EC.
            presence_of_element_located
            ((By.CSS_SELECTOR, f"a[href*='{subcategory_href}']"))
        )
        """ Кликаем через JavaScript - самый надёжный способ """
        self.driver.execute_script(f"""
            var link = document.querySelector('a[href*="{subcategory_href}"]');
            if (link) {{
                link.click();
            }} else {{
                throw new Error
                ('Подкатегория с href "{subcategory_href}" не найдена');
            }}
        """)
        return CatalogPage(self.driver, self.wait)


class SearchResultsPage:
    """Страница с результатами поиска."""

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    @allure.step("Ожидание загрузки результатов поиска")
    def wait_for_results(self):
        """Ожидает появления либо
         карточек товаров, либо заглушки «ничего не найдено»."""
        self.wait.until(
            lambda d: (
                d.find_elements
                (By.CSS_SELECTOR, ".product-card, article,"
                                  " .products-list__item")
                or d.find_elements(By.CSS_SELECTOR, ".search-title__head")
            )
        )
        return self

    def is_no_results_found(self):
        """Возвращает True, если отображается
         любой из признаков отсутствия товаров."""
        try:
            # Проверяем заголовок h1
            (self.
             wait.until(EC.
                        presence_of_element_located((By.CSS_SELECTOR,
                                                     "h1.search-title__head"
                                                     ))))
            if ("не принес результатов" in self.
                    driver.find_element(By.CSS_SELECTOR,
                                        "h1.search-title__head").text):
                return True
        except TimeoutException:
            pass

        try:
            # Проверяем заглушку h4
            (self.
             wait.until(EC.
                        visibility_of_element_located((By.
                                                       CSS_SELECTOR,
                                                       "h4.catalog-stub__title"
                                                       ))))
            if ("Похоже, у нас такого нет" in self.
                    driver.find_element(By.CSS_SELECTOR,
                                        "h4.catalog-stub__title").text):
                return True
        except TimeoutException:
            pass

        return False

    @allure.step("Проверить наличие товаров в результате поиска")
    def has_products(self) -> bool:
        """Возвращает True, если на странице есть
         хотя бы одна карточка товара."""
        products = (self
                    .driver.find_elements
                    (By.CSS_SELECTOR, ".product-card, article,"
                                      " .products-list__item"))
        return len(products) > 0

    @allure.step("Проверить, что результат поиска пуст")
    def is_empty_result(self) -> bool:
        """Возвращает True, если отображается заглушка
         об отсутствии товаров."""
        try:
            self.wait.until(
                EC.
                visibility_of_element_located
                ((By.CSS_SELECTOR, ".catalog-stub__title"))
            )
            self.wait.until(
                lambda d: d.execute_script(
                    "var el = document.querySelector('.catalog-stub__title');"
                    "return el && el.textContent.trim() !== '';"
                )
            )
            return True
        except TimeoutException:
            return False

    @allure.step("Добавить первый найденный товар в корзину")
    def add_first_product_to_cart(self):
        wait = (WebDriverWait
                (self.driver, 10,
                 ignored_exceptions=[StaleElementReferenceException]))

        def click_buy_button(driver):
            """ Ищем элемент заново при каждой итерации """
            btn = (driver.find_element
                   (By.CSS_SELECTOR, "[data-testid-button-mini-product-card="
                                     "'canBuy']"))
            """ JavaScript-клик устойчив к изменениям DOM """
            driver.execute_script("arguments[0].click();", btn)
            return True

        wait.until(click_buy_button)
        return self

    @allure.step("Получить значение счётчика товаров в корзине"
                 " (рядом с иконкой)")
    def get_cart_counter(self) -> int:
        """Возвращает число, отображаемое на иконке корзины."""
        try:
            counter = self.wait.until(
                EC.
                presence_of_element_located
                ((By.CSS_SELECTOR, ".header-cart__counter,"
                                   " .cart-badge__count"))
            )
            return int(counter.text.strip())
        except TimeoutException:
            return 0

    @allure.step("Перейти в корзину")
    def open_cart(self):
        """Кликает по иконке корзины в шапке."""
        cart_icon = self.wait.until(
            EC.
            element_to_be_clickable
            ((By.CSS_SELECTOR,
              "button[data-testid-button-header='cart']"))
        )
        cart_icon.click()
        return CartPage(self.driver, self.wait)


class CartPage:
    """Страница корзины."""

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    @allure.step("Ожидание загрузки страницы корзины")
    def is_loaded(self):
        """Ожидает, что URL содержит /cart и присутствуют элементы корзины."""
        self.wait.until(EC.url_contains("/cart"))
        self.wait.until(
            EC.
            presence_of_element_located
            ((By.CSS_SELECTOR, ".cart-title,"
                               " .cart-item, .cart-product"))
        )
        return self

    @allure.step("Проверить, есть ли товары в корзине")
    def has_items(self) -> bool:
        """Возвращает True, если в корзине есть хотя бы один товар."""
        items = (self.
                 driver.find_elements
                 (By.CSS_SELECTOR, ".cart-item, .cart-product,"
                                   " [data-testid='cart-item']"))
        return len(items) > 0

    @allure.step("Удалить первый товар из корзины")
    def remove_first_item(self):
        """Кликает по кнопке удаления первого товара."""
        remove_btn = self.wait.until(
            EC.
            element_to_be_clickable
            ((By.CSS_SELECTOR, "button[data-testid-button-cart="
                               "'removeProduct']"))
        )
        remove_btn.click()
        return self

    @allure.step("Проверить, что корзина пуста")
    def is_empty(self) -> bool:
        """Возвращает True, если отображается сообщение о пустой корзине."""
        try:
            self.wait.until(
                EC.
                visibility_of_element_located
                ((By.CSS_SELECTOR, ".cart-item-deleted__title"))
            )
            self.wait.until(
                EC.
                invisibility_of_element_located
                ((By.CSS_SELECTOR, "button[data-testid-button-cart="
                                   "'removeProduct']"))
            )
            return True
        except TimeoutException:
            return False


class CatalogPage:
    """Страница каталога (после выбора категории/подкатегории)."""

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    @allure.step("Ожидание загрузки страницы каталога")
    def is_loaded(self):
        """Ожидает появления элементов каталога (заголовок или товары)."""
        self.wait.until(
            EC.presence_of_element_located
            ((By.CSS_SELECTOR, ".catalog-title,"
                               " .product-card,"
                               " .products-list__item"))
        )
        return self

    @allure.step("Проверить наличие товаров в каталоге")
    def has_products(self) -> bool:
        """Возвращает True, если в текущей категории есть товары."""
        products = (
            self.driver.find_elements
            (By.CSS_SELECTOR, ".product-card,"
                              " .products-list__item"))
        return len(products) > 0
