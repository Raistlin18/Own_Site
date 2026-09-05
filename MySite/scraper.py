import requests
import re
from dataclasses import dataclass
from urllib.parse import quote

from bs4 import BeautifulSoup


REQUEST_TIMEOUT_SECONDS = 10
RESULT_LIMIT = 10
REQUEST_HEADERS = {"User-Agent": "Mozilla/5.0 (compatible; ProductFinder/1.0)"}


class ScraperError(Exception):
    """Raised when a product search cannot be completed safely."""


@dataclass(frozen=True)
class ProductResult:
    name: str
    price: int
    url: str
    currency: str


def fetch_page(url):
    try:
        response = requests.get(
            url,
            headers=REQUEST_HEADERS,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        raise ScraperError("eMAG is currently unavailable. Please try again later.") from exc

    return response.text


def parse_price(price_element):
    if price_element is None:
        return None

    numeric_price = re.sub(r"[^\d]", "", price_element.get_text())
    return int(numeric_price) if numeric_price else None


def parse_emag_products(html):
    document = BeautifulSoup(html, "html.parser")
    products = []

    for container in document.select(".card-item.card-standard"):
        title = container.select_one("a.card-v2-title")
        price = parse_price(container.select_one(".product-new-price"))
        if title is None or price is None or not title.get("href"):
            continue

        products.append(
            ProductResult(name=title.get_text(strip=True), price=price, url=title["href"], currency="Ft")
        )

    return products


def get_items(product):
    products = parse_emag_products(fetch_page(f"https://www.emag.hu/search/{quote(product)}"))

    unique_products = {product.url: product for product in products}
    return sorted(unique_products.values(), key=lambda product: product.price)[:RESULT_LIMIT]
