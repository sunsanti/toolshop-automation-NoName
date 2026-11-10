import re
import uuid

import pytest
from playwright.sync_api import Page, expect

from pages.contact_page import ContactPage
from pages.home_page import HomePage
from pages.login_page import LoginPage


@pytest.mark.smoke
def test_search_pliers(page: Page):
    """Goal: searching "pliers" only shows matching products.
    Precondition: home page is open with the product list loaded.
    Expected: every product name shown contains "pliers".
    """
    home = HomePage(page).open().search("pliers")

    expect(home.search_completed).to_be_attached()
    expect(home.product_names.first).to_be_visible()
    names = home.product_names.all_inner_texts()
    assert names, "no products found"
    assert all("pliers" in name.lower() for name in names), names


@pytest.mark.smoke
def test_add_claw_hammer_to_cart(page: Page):
    """Goal: adding a product with quantity 3 updates the cart badge.
    Precondition: home page is open, cart is empty.
    Expected: the cart badge in the menu shows 3.
    """
    product = HomePage(page).open().open_product("Claw Hammer").add_to_cart(3)

    expect(product.cart_quantity).to_have_text("3")


@pytest.mark.smoke
def test_login_with_unknown_email(page: Page):
    """Goal: login with an email that does not exist is rejected.
    Precondition: login page is open; the email is random (never the shared customer account).
    Expected: "Invalid email or password" is shown and the URL still ends with /auth/login.
    """
    login = LoginPage(page).open().login(f"nobody-{uuid.uuid4().hex[:12]}@example.com", "WrongPass123!")

    expect(login.error).to_have_text("Invalid email or password")
    expect(page).to_have_url(re.compile(r"/auth/login$"))


@pytest.mark.smoke
def test_contact_form_empty(page: Page):
    """Goal: sending an empty contact form shows required-field errors.
    Precondition: contact page is open, no field filled.
    Expected: "Subject is required" and "Message is required" are shown.
    """
    contact = ContactPage(page).open().submit()

    expect(contact.errors).to_contain_text(["Subject is required", "Message is required"])
