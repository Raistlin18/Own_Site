import requests
import re
from dataclasses import dataclass
from urllib.parse import quote, urljoin

from bs4 import BeautifulSoup


REQUEST_TIMEOUT_SECONDS = 10
MAX_PAGES = 5
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


def fetch_page(url, params=None):
    try:
        response = requests.get(
            url,
            params=params,
            headers=REQUEST_HEADERS,
            timeout=REQUEST_TIMEOUT_SECONDS,
        )
        response.raise_for_status()
    except requests.RequestException as exc:
        if exc.response is not None and exc.response.status_code == 403:
            raise ScraperError(
                "The selected store is blocking automated requests. Please try another store."
            ) from exc
        raise ScraperError("The product source is currently unavailable.") from exc

    return response.text


def get_page_count(html):
    document = BeautifulSoup(html, "html.parser")
    page_count = document.select_one(".list-tool-pagination-text strong")
    if page_count is None:
        return 1

    match = re.search(r"/\s*(\d+)", page_count.get_text(strip=True))
    return int(match.group(1)) if match else 1


def parse_price(price_element):
    if price_element is None:
        return None

    numeric_price = re.sub(r"[^\d]", "", price_element.get_text())
    return int(numeric_price) if numeric_price else None


def parse_newegg_products(html):
    document = BeautifulSoup(html, "html.parser")
    products = []

    for container in document.select(".item-container"):
        title = container.select_one("a.item-title")
        price = parse_price(container.select_one(".price-current strong"))
        if title is None or price is None or not title.get("href"):
            continue

        products.append(
            ProductResult(name=title.get_text(strip=True), price=price, url=title["href"], currency="$")
        )

    return products


def parse_alza_products(html):
    document = BeautifulSoup(html, "html.parser")
    products = []

    for container in document.select(".browsingitem"):
        title = container.select_one("a.name")
        price = parse_price(container.select_one(".price"))
        if title is None or price is None or not title.get("href"):
            continue

        products.append(
            ProductResult(
                name=title.get_text(strip=True),
                price=price,
                url=urljoin("https://www.alza.hu", title["href"]),
                currency="Ft",
            )
        )

    return products


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


def search_newegg(product):
    first_page = fetch_page(
        "https://www.newegg.com/p/pl", {"d": product, "N": "4131", "page": 1}
    )
    products = parse_newegg_products(first_page)
    page_count = min(get_page_count(first_page), MAX_PAGES)

    for page in range(2, page_count + 1):
        products.extend(
            parse_newegg_products(
                fetch_page("https://www.newegg.com/p/pl", {"d": product, "N": "4131", "page": page})
            )
        )

    return products


def search_alza(product):
    return parse_alza_products(
        fetch_page("https://www.alza.hu/search.htm", {"exps": product})
    )


def search_emag(product):
    return parse_emag_products(fetch_page(f"https://www.emag.hu/search/{quote(product)}"))


SEARCHERS = {
    "newegg": search_newegg,
    "alza": search_alza,
    "emag": search_emag,
}


def get_items(store, product):
    try:
        products = SEARCHERS[store](product)
    except KeyError as exc:
        raise ScraperError("The selected store is not supported.") from exc

    unique_products = {product.url: product for product in products}
    return sorted(unique_products.values(), key=lambda product: product.price)[:RESULT_LIMIT]
