import json
import re

import pytest
from playwright.sync_api import expect

from pages.home_page import PRODUCT_LIST, HomePage

pytestmark = pytest.mark.ui

EMPTY_PAGE = {"current_page": 1, "data": [], "from": None, "last_page": 1,
              "per_page": 9, "to": None, "total": 0}


def test_home_without_images_still_lists_products(page):
    """Goal: the page works when image requests are blocked.
    Precondition: every image request is aborted by page.route.
    Expected: product names visible and at least one image request was aborted."""
    blocked = []

    def block(route):
        blocked.append(route.request.url)
        route.abort()

    page.route(re.compile(r"\.(png|jpe?g|webp|avif|svg)(\?.*)?$"), block)
    home = HomePage(page).open()
    expect(home.product_names.first).to_be_visible()
    assert blocked, "no image request was blocked"


def test_home_with_empty_product_list_shows_no_results(page):
    """Goal: empty state of the product grid.
    Precondition: product list API mocked with an empty page.
    Expected: 'There are no products found.' and 0 product cards."""
    page.route(PRODUCT_LIST, lambda route: route.fulfill(
        status=200, content_type="application/json", body=json.dumps(EMPTY_PAGE)))
    home = HomePage(page).open()
    expect(home.no_results).to_have_text("There are no products found.")
    expect(home.product_names).to_have_count(0)
