# Lab 4A. Task 1 - The cart that belongs to everybody
# Student: Javohir Gayratov
#
# 1.1 Question: Write a pytest test that reproduces the ticket: create two carts, add a product
#     and a coupon to the first one, and check that the second one is still empty. The test must
#     fail on the code above.
#     Answer: test_old_cart_reproduces_ticket_4127 makes two carts of the old class, adds 'A1'
#     and 'SALE10' to the first one and checks that the second one is empty. On the old code
#     this check fails, so the test expects AssertionError. The same check passes for my Cart.
#
# 1.2 Question: The class has two bugs with the same root cause. Find both and name the root
#     cause in one sentence.
#     Answer: Bug 1: items = [] is a class attribute, so every Cart object uses the same list.
#     Bug 2: coupons=[] is evaluated only once, when def runs, so every cart created without
#     coupons gets the same default list. Root cause: one mutable list is created once and
#     shared by all objects, instead of a new list for every object.
#
# 1.3 Question: Fix both bugs. Then rewrite Cart as a @dataclass. What happens if you write
#     coupons: list = [] in a dataclass, and what do you write instead?
#     Answer: The lists are now created in __init__ (coupons=None -> new list). In a dataclass
#     coupons: list = [] does not work at all, Python raises "ValueError: mutable default
#     <class 'list'> for field coupons is not allowed: use default_factory". Instead we write
#     coupons: list = field(default_factory=list).
#
# 1.4 Question: Look again at the quick check on slide 15. Why does self.items.append(...)
#     change the data of every cart, while self.count += 1 creates a new attribute on one
#     object only?
#     Answer: self.items.append(...) only reads the name items. The object has no own items, so
#     Python finds the list on the class and changes this shared list. self.count += 1 is
#     self.count = self.count + 1, and an assignment through self always creates an attribute
#     on this one object, so the value on the class stays the same.
from dataclasses import dataclass, field

import pytest


# old code from ticket #4127, only to show the bug
class OldCart:
    items = []

    def __init__(self, user_id, coupons=[]):
        self.user_id = user_id
        self.coupons = coupons

    def add(self, sku, qty=1):
        self.items.append((sku, qty))

    def apply_coupon(self, code):
        self.coupons.append(code)


# fix 1: every cart gets its own lists in __init__
class FixedCart:

    def __init__(self, user_id, coupons=None):
        self.user_id = user_id
        self.items = []
        self.coupons = list(coupons) if coupons is not None else []

    def add(self, sku, qty=1):
        self.items.append((sku, qty))

    def apply_coupon(self, code):
        self.coupons.append(code)


# fix 2: the same cart as a dataclass
@dataclass
class Cart:
    user_id: int
    coupons: list = field(default_factory=list)
    items: list = field(default_factory=list)

    def add(self, sku, qty=1):
        self.items.append((sku, qty))

    def apply_coupon(self, code):
        self.coupons.append(code)


def check_two_carts_are_separate(cart_class):
    first = cart_class(1)
    second = cart_class(2)
    first.add("A1", 2)
    first.apply_coupon("SALE10")
    assert second.items == []
    assert second.coupons == []


def test_old_cart_reproduces_ticket_4127():
    # with the old cart the second cart sees the product and coupon of the first one
    with pytest.raises(AssertionError):
        check_two_carts_are_separate(OldCart)
    OldCart.items.clear()   # clean the shared list so other tests are not affected


@pytest.mark.parametrize("cart_class", [FixedCart, Cart])
def test_two_carts_never_share_lists(cart_class):
    check_two_carts_are_separate(cart_class)


@pytest.mark.parametrize("cart_class", [FixedCart, Cart])
def test_new_carts_start_empty_after_other_carts_were_used(cart_class):
    used = cart_class(1)
    used.add("B7")
    used.apply_coupon("WELCOME")
    fresh = cart_class(2)
    assert fresh.items == [] and fresh.coupons == []
    assert used.items is not fresh.items
    assert used.coupons is not fresh.coupons


def test_fixed_cart_copies_coupons_it_receives():
    start_coupons = ["WELCOME"]
    cart = FixedCart(1, start_coupons)
    cart.apply_coupon("SALE10")
    assert start_coupons == ["WELCOME"]


def test_dataclass_does_not_allow_list_default():
    with pytest.raises(ValueError, match="mutable default"):
        @dataclass
        class BadCart:
            user_id: int
            coupons: list = []


def test_quick_check_from_slide_15():
    class Counter:
        count = 0
        items = []

    a, b = Counter(), Counter()
    a.items.append("x")      # changes the one list on the class
    a.count += 1             # creates a.count, Counter.count is still 0
    assert b.items == ["x"]
    assert a.count == 1 and b.count == 0 and Counter.count == 0
    assert "count" in vars(a) and "items" not in vars(a)
