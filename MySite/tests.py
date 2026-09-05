from django.test import TestCase
from django.urls import reverse
from unittest.mock import patch

from .scraper import (
    ProductResult,
    get_items,
    parse_emag_products,
)


EMAG_PAGE = """
<div class="card-item card-standard">
  <a class="card-v2-title" href="https://www.emag.hu/cheap-keyboard/pd/ABC/">Compact keyboard</a>
  <p class="product-new-price">19.990 <span>Ft</span></p>
</div>
"""


class ScraperTests(TestCase):
    def test_parse_emag_products_uses_forint(self):
        products = parse_emag_products(EMAG_PAGE)

        self.assertEqual(products[0].name, "Compact keyboard")
        self.assertEqual(products[0].price, 19990)
        self.assertEqual(products[0].currency, "Ft")

    @patch("MySite.scraper.fetch_page", return_value=EMAG_PAGE)
    def test_get_items_sorts_and_limits_unique_products(self, mock_fetch):
        products = get_items("keyboard")

        self.assertEqual([product.price for product in products], [19990])
        mock_fetch.assert_called_once_with("https://www.emag.hu/search/keyboard")


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

        response = self.client.post(reverse("scraper"), {"product": " keyboard "})

        self.assertContains(response, "Compact keyboard")
        mock_get_items.assert_called_once_with("keyboard")
