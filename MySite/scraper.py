import requests
import re
from dataclasses import dataclass

from bs4 import BeautifulSoup


SEARCH_URL = "https://www.newegg.com/p/pl"
REQUEST_TIMEOUT_SECONDS = 10
MAX_PAGES = 5
RESULT_LIMIT = 10


class ScraperError(Exception):
    """Raised when a product search cannot be completed safely."""


@dataclass(frozen=True)
class ProductResult:
    name: str
    price: int
    url: str


def fetch_search_page(product, page):
    try:
        response = requests.get(
            SEARCH_URL,
            params={"d": product, "N": "4131", "page": page},
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ScraperError("The product source is currently unavailable.") from exc

    return response.text


def get_page_count(html):
    document = BeautifulSoup(html, "html.parser")
    page_count = document.select_one(".list-tool-pagination-text strong")
    if page_count is None:
        return 1

    match = re.search(r"/\s*(\d+)", page_count.get_text(strip=True))
    return int(match.group(1)) if match else 1


def parse_price(product_container):
    price_element = product_container.select_one(".price-current strong")
    if price_element is None:
        return None

    numeric_price = re.sub(r"[^\d]", "", price_element.get_text())
    return int(numeric_price) if numeric_price else None


def parse_products(html):
    document = BeautifulSoup(html, "html.parser")
    products = []

    for container in document.select(".item-container"):
        title = container.select_one("a.item-title")
        price = parse_price(container)
        if title is None or price is None or not title.get("href"):
            continue

        products.append(
            ProductResult(name=title.get_text(strip=True), price=price, url=title["href"])
        )

    return products


def get_items(product):
    first_page = fetch_search_page(product, page=1)
    products = parse_products(first_page)
    page_count = min(get_page_count(first_page), MAX_PAGES)

    for page in range(2, page_count + 1):
        products.extend(parse_products(fetch_search_page(product, page)))

    unique_products = {product.url: product for product in products}
    return sorted(unique_products.values(), key=lambda product: product.price)[:RESULT_LIMIT]
