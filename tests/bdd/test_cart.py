"""BDD: search a product -> add to cart -> cart computes the right price.

Step definitions only call page objects (locators live in pages/).
Run:  pytest tests/bdd -v   (each Examples row is its own test)
"""
import pytest
from playwright.sync_api import expect
from pytest_bdd import given, parsers, scenarios, then, when

from pages.home_page import HomePage

pytestmark = [pytest.mark.bdd, pytest.mark.ui]

scenarios("cart.feature")


@given("I am on the home page", target_fixture="home")
def home(page):
    home = HomePage(page).open()
    expect(home.product_names.first).to_be_visible()
    return home


@when(parsers.parse('I open the product "{product}"'), target_fixture="product_page")
def open_product(home, product):
    product_page = home.open_product(product)
    expect(product_page.name).to_have_text(product)
    return product_page


@when(parsers.parse("I add it to the cart with quantity {quantity:d}"), target_fixture="unit_price")
def add_to_cart(product_page, quantity):
    unit_price = product_page.price()  # read before adding, keep it for the Then steps
    product_page.add_to_cart(quantity=quantity)
    expect(product_page.cart_quantity).to_have_text(str(quantity))
    return unit_price


@when("I go to my cart", target_fixture="cart")
def go_to_cart(product_page):
    return product_page.go_to_cart()


@then(parsers.parse('the cart has 1 line for "{product}"'))
def one_line(cart, product):
    expect(cart.product_titles).to_have_count(1)
    expect(cart.product_titles.first).to_have_text(product)


@then(parsers.parse("the line price is the unit price times {quantity:d}"))
def line_price(cart, unit_price, quantity):
    assert cart.line_totals() == [pytest.approx(unit_price * quantity)]


@then("the cart total is the sum of the line prices")
def total(cart):
    assert cart.total_value() == pytest.approx(sum(cart.line_totals()))
