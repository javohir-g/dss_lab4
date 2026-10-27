# Lab 4A. Task 5 - Validation without touching 40 call sites
# Student: Javohir Gayratov
#
# 5.1 Question: Turn price and discount_percent into properties with setters (slide 22).
#     Rules: price is an int greater than 0; discount_percent is an int from 0 to 90.
#     Answer: Done below. The 40 call sites still write product.price = ..., but now it goes
#     through the setter and the setter checks the rule, so no call site has to change.
#
# 5.2 Question: Make sure a wrong value is rejected by the constructor as well, not only by
#     later assignments.
#     Answer: __init__ writes self.price = price (not self._price), so the constructor also
#     goes through the setters and Product('A1', -5) raises ValueError.
#
# 5.3 Question: final_price() must return an int in sum, rounded down. Today
#     Product('A1', 99_990, 15).final_price() returns 84991.5.
#     Answer: final_price() uses only int math: price * (100 - discount) // 100, and // rounds
#     down, so now it returns 84991.
#
# 5.4 Question: A teammate proposes to compute the final price once in __init__ and keep it in
#     an attribute. Show in three lines of code what goes wrong when the price changes later.
#     Answer: The saved final price is a copy and nobody updates it when the price changes:
#         p = TeammateProduct("A1", 100_000, 10)   # final_price = 90 000
#         p.price = 200_000
#         print(p.final_price)                     # 90000, but it should be 180000
#     So final_price() must stay a method that calculates from the current price.
#
# 5.5 Question: The sku must never change after the object is created. Make it read-only.
#     Answer: sku is a property without a setter, so p.sku = 'X' raises AttributeError.
import pytest


class Product:
    MAX_DISCOUNT_PERCENT = 90

    def __init__(self, sku, price, discount_percent=0):
        self._sku = sku
        self.price = price                        # goes through the setter
        self.discount_percent = discount_percent  # goes through the setter

    @property
    def sku(self):
        return self._sku

    @property
    def price(self):
        return self._price

    @price.setter
    def price(self, value):
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"price must be an int in sum, got {value!r}")
        if value <= 0:
            raise ValueError(f"price must be greater than 0, got {value}")
        self._price = value

    @property
    def discount_percent(self):
        return self._discount_percent

    @discount_percent.setter
    def discount_percent(self, value):
        if isinstance(value, bool) or not isinstance(value, int):
            raise TypeError(f"discount_percent must be an int, got {value!r}")
        if not 0 <= value <= self.MAX_DISCOUNT_PERCENT:
            raise ValueError(f"discount_percent must be 0..{self.MAX_DISCOUNT_PERCENT}, got {value}")
        self._discount_percent = value

    def final_price(self) -> int:
        return self.price * (100 - self.discount_percent) // 100


# teammate's version from 5.4 (final price is saved once in __init__)
class TeammateProduct:

    def __init__(self, sku, price, discount_percent=0):
        self.sku = sku
        self.price = price
        self.discount_percent = discount_percent
        self.final_price = price * (100 - discount_percent) // 100


def test_final_price_is_int_rounded_down():
    price = Product("A1", 99_990, 15).final_price()
    assert price == 84_991 and type(price) is int


def test_old_assignment_still_works():
    p = Product("A1", 100_000)
    p.price = 120_000
    p.discount_percent = 10
    assert p.final_price() == 108_000


@pytest.mark.parametrize("value", [0, -1])
def test_bad_price_assignment(value):
    p = Product("A1", 100_000)
    with pytest.raises(ValueError):
        p.price = value
    assert p.price == 100_000


@pytest.mark.parametrize("value", [-1, 91, 150])
def test_bad_discount_assignment(value):
    p = Product("A1", 100_000)
    with pytest.raises(ValueError):
        p.discount_percent = value
    assert p.discount_percent == 0


def test_discount_limits_are_allowed():
    assert Product("A1", 1_000, 0).final_price() == 1_000
    assert Product("A1", 1_000, 90).final_price() == 100


def test_constructor_validates_too():
    with pytest.raises(ValueError):
        Product("A1", -5)
    with pytest.raises(ValueError):
        Product("A1", 0)
    with pytest.raises(ValueError):
        Product("A1", 1_000, 150)
    with pytest.raises(TypeError):
        Product("A1", 99.9)


def test_sku_is_read_only():
    p = Product("A1", 1_000)
    with pytest.raises(AttributeError):
        p.sku = "X"
    assert p.sku == "A1"


def test_teammate_cached_final_price_goes_stale():
    p = TeammateProduct("A1", 100_000, 10)   # final_price is stored as 90 000
    p.price = 200_000                        # one of the 40 call sites changes the price
    assert p.final_price == 90_000           # still the old value, should be 180 000
