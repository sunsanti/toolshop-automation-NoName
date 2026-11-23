Feature: Shopping cart price
  As a shopper
  I want the cart to compute the price of what I buy
  So that I know exactly how much I will pay

  Scenario Outline: Cart line price is unit price times quantity
    Given I am on the home page
    When I open the product "<product>"
    And I add it to the cart with quantity <quantity>
    And I go to my cart
    Then the cart has 1 line for "<product>"
    And the line price is the unit price times <quantity>
    And the cart total is the sum of the line prices

    Examples:
      | product            | quantity |
      | Combination Pliers | 1        |
      | Claw Hammer        | 3        |
