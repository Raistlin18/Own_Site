from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

from .scraper import (
    ProductResult,
    ScraperError,
    get_items,
    get_page_count,
    parse_alza_products,
    parse_emag_products,
    parse_newegg_products,
)


SAMPLE_PAGE = """
<div class="list-tool-pagination-text"><strong>1/1</strong></div>
<div class="item-container">
  <a class="item-title" href="https://example.com/expensive">Gaming keyboard</a>
  <li class="price-current"><strong>1,299</strong></li>
</div>
<div class="item-container">
  <a class="item-title" href="https://example.com/cheap">Compact keyboard</a>
  <li class="price-current"><strong>99</strong></li>
</div>
"""

ALZA_PAGE = """
<div class="browsingitem">
  <a class="name" href="/cheap-keyboard.htm">Compact keyboard</a>
  <span class="price">19 990 Ft</span>
</div>
"""

EMAG_PAGE = """
<div class="card-item card-standard">
  <a class="card-v2-title" href="https://www.emag.hu/cheap-keyboard/pd/ABC/">Compact keyboard</a>
  <p class="product-new-price">19.990 <span>Ft</span></p>
</div>
"""


class ScraperTests(TestCase):
    def test_get_page_count_falls_back_to_one(self):
        self.assertEqual(get_page_count("<html></html>"), 1)

    def test_parse_newegg_products_ignores_incomplete_products(self):
        products = parse_newegg_products(SAMPLE_PAGE + '<div class="item-container"></div>')

        self.assertEqual(len(products), 2)
        self.assertEqual(products[0].name, "Gaming keyboard")
        self.assertEqual(products[0].price, 1299)
        self.assertEqual(products[0].currency, "$")

    def test_parse_alza_products_uses_forint_and_absolute_url(self):
        products = parse_alza_products(ALZA_PAGE)

        self.assertEqual(products[0].price, 19990)
        self.assertEqual(products[0].currency, "Ft")
        self.assertEqual(products[0].url, "https://www.alza.hu/cheap-keyboard.htm")

    def test_parse_emag_products_uses_forint(self):
        products = parse_emag_products(EMAG_PAGE)

        self.assertEqual(products[0].name, "Compact keyboard")
        self.assertEqual(products[0].price, 19990)
        self.assertEqual(products[0].currency, "Ft")

    @patch("MySite.scraper.fetch_page", return_value=SAMPLE_PAGE)
    def test_get_items_sorts_and_limits_unique_products(self, mock_fetch):
        products = get_items("newegg", "keyboard")

        self.assertEqual([product.price for product in products], [99, 1299])
        mock_fetch.assert_called_once_with(
            "https://www.newegg.com/p/pl", {"d": "keyboard", "N": "4131", "page": 1}
        )

    def test_get_items_rejects_unknown_store(self):
        with self.assertRaises(ScraperError):
            get_items("unknown", "keyboard")


class ScraperViewTests(TestCase):
    def test_get_request_renders_empty_search_form(self):
        response = self.client.get(reverse("scraper"))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Product Finder")

    def test_invalid_search_does_not_call_scraper(self):
        with patch("MySite.views.get_items") as mock_get_items:
            response = self.client.post(reverse("scraper"), {"product": ""})

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "This field is required.")
        mock_get_items.assert_not_called()

    @patch("MySite.views.get_items")
    def test_valid_search_renders_product_results(self, mock_get_items):
        mock_get_items.return_value = [
            ProductResult("Compact keyboard", 99, "https://example.com/cheap", "Ft")
        ]

        response = self.client.post(
            reverse("scraper"), {"store": "emag", "product": " keyboard "}
        )

        self.assertContains(response, "Compact keyboard")
        mock_get_items.assert_called_once_with("emag", "keyboard")
