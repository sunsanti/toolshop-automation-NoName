import re

import pytest
from playwright.sync_api import expect

from pages.account_page import AccountPage
from pages.contact_page import ContactPage
from pages.home_page import HomePage
from pages.login_page import LoginPage

pytestmark = pytest.mark.ui


# ---------------------------------------------------------------- Listing and search
def test_search_unknown_keyword_shows_no_results_message(page):
    """Goal: empty search state.
    Precondition: home page is open.
    Expected: 'There are no products found.' and zero product cards."""
    home = HomePage(page).open().search("zzz-no-such-tool")
    expect(home.no_results).to_have_text("There are no products found.")
    expect(home.product_names).to_have_count(0)


@pytest.mark.parametrize("order", ["price,asc", "price,desc"])
def test_sort_by_price_orders_products(page, order):
    """Goal: sorting by price.
    Precondition: home page is open with the product list loaded.
    Expected: prices on the first page are sorted in the chosen direction."""
    home = HomePage(page).open()
    expect(home.product_names.first).to_be_visible()
    home.sort_by(order)
    expect(home.sorting_completed).to_be_attached()
    prices = home.prices()
    assert prices == sorted(prices, reverse=order.endswith("desc")), prices


def test_price_slider_lower_max_reloads_cheaper_products(page):
    """Goal: the price slider filters the list (slider situation).
    Precondition: home page is open; right handle moved left 3 steps with the keyboard.
    Expected: the handle shows the new max and no product shown costs more than it."""
    home = HomePage(page).open()
    expect(home.product_names.first).to_be_visible()
    new_max = home.lower_max_price(3)
    expect(home.price_slider_max).to_have_attribute("aria-valuenow", str(new_max))
    expect(home.product_names.first).to_be_visible()
    assert all(p <= new_max for p in home.prices()), home.prices()


# ---------------------------------------------------------------- Filter
def test_filter_category_hammer_shows_only_hammers(page):
    """Goal: category filter.
    Precondition: home page is open; category 'Hammer' is ticked.
    Expected: at least one product and every name contains 'hammer'."""
    home = HomePage(page).open().filter_by_category("Hammer")
    expect(home.filter_completed).to_be_attached()
    names = home.product_names.all_inner_texts()
    assert names, "filter returned no products"
    assert all("hammer" in n.lower() for n in names), names


# ---------------------------------------------------------------- Product detail
@pytest.mark.smoke
def test_product_detail_shows_clicked_name_and_price(page):
    """Goal: the detail page belongs to the product that was clicked.
    Precondition: home page is open; the first product card is clicked.
    Expected: detail page shows the same name and the same price as the card."""
    home = HomePage(page).open()
    expect(home.product_names.first).to_be_visible()
    name, price = home.product_names.first.inner_text().strip(), home.prices()[0]
    product = home.open_product(name)
    expect(product.name).to_have_text(name)
    assert product.price() == pytest.approx(price)


# ---------------------------------------------------------------- Cart
def test_cart_line_price_equals_unit_price_times_quantity(page):
    """Goal: cart arithmetic.
    Precondition: empty cart (new context per test); 2 x 'Combination Pliers' added.
    Expected: line price = unit price x 2 and total = sum of the lines."""
    product = HomePage(page).open().open_product("Combination Pliers")
    unit = product.price()
    product.add_to_cart(quantity=2)
    expect(product.cart_quantity).to_have_text("2")
    cart = product.go_to_cart()
    expect(cart.product_titles).to_have_count(1)
    assert cart.line_totals() == [pytest.approx(unit * 2)]
    assert cart.total_value() == pytest.approx(sum(cart.line_totals()))


def test_cart_continue_shopping_returns_to_home(page):
    """Goal: 'Continue Shopping' leaves the cart.
    Precondition: 'Hammer' is in the cart and the cart page is open.
    Expected: the product grid is visible again."""
    cart = HomePage(page).open().open_product("Hammer").add_to_cart().go_to_cart()
    expect(cart.product_titles.first).to_have_text("Hammer")
    cart.continue_shopping.click()
    expect(HomePage(page).product_names.first).to_be_visible()


# ---------------------------------------------------------------- Authentication
def test_login_empty_form_shows_required_errors(page):
    """Goal: client-side validation of the login form.
    Precondition: login page is open, both fields empty.
    Expected: 'Email is required' and 'Password is required'."""
    login = LoginPage(page).open().login("", "")
    expect(login.email_error).to_contain_text("Email is required")
    expect(login.password_error).to_contain_text("Password is required")


# ---------------------------------------------------------------- Contact and account
@pytest.mark.smoke
def test_account_page_logged_in_shows_user_menu(logged_in_page):
    """Goal: reuse the saved login (storage_state from auth_state).
    Precondition: logged_in_page, no login form in this test.
    Expected: title 'My account' and the user menu shows 'QA Bot'."""
    account = AccountPage(logged_in_page).open()
    expect(account.title).to_have_text("My account")
    expect(account.nav_menu).to_contain_text("QA Bot")


def _fill_contact(page, attachment):
    return (ContactPage(page).open()
            .fill_form("QA", "Bot", "qa@example.com", "customer-service",
                       "Automated test message, long enough to pass validation.")
            .attach(attachment)
            .submit())


def test_contact_empty_attachment_is_sent(page, tmp_path):
    """Goal: file upload on the contact form.
    Precondition: form filled, an empty (0 byte) file attached.
    Expected: the success message 'Thanks for your message!' is shown."""
    empty = tmp_path / "empty.txt"
    empty.write_bytes(b"")
    contact = _fill_contact(page, empty)
    expect(contact.success).to_contain_text("Thanks for your message!")


def test_contact_non_empty_attachment_is_rejected(page, tmp_path):
    """Goal: Toolshop only accepts empty files.
    Precondition: form filled, a file with content attached.
    Expected: attachment error 'File should be empty.'."""
    full = tmp_path / "notes.txt"
    full.write_text("hello")
    contact = _fill_contact(page, full)
    expect(contact.attachment_error).to_have_text("File should be empty.")


def test_footer_github_link_opens_new_tab(page):
    """Goal: external link opens in a new tab.
    Precondition: home page is open.
    Expected: a new tab opens on github.com/testsmith-io/practice-software-testing."""
    new_tab = HomePage(page).open().open_github_in_new_tab()
    expect(new_tab).to_have_url(re.compile(r"github\.com/testsmith-io/practice-software-testing"))
