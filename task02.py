# Lab 4A. Task 2 - Three different delivery fees
# Student: Javohir Gayratov
#
# 2.1 Question: Work out by hand what each service returns for three orders: 150 000 sum at
#     4.2 km, 90 000 sum at 4.2 km and 90 000 sum at 3.6 km. Which service follows the rule in
#     each case? Then run the code to check yourself.
#     Answer: By the rule: 150 000 / 4.2 km = 0; 90 000 / 4.2 km = 12 000 + 2 * 3 000 = 18 000
#     (1.2 extra km = 2 started km); 90 000 / 3.6 km = 12 000 + 1 * 3 000 = 15 000.
#     Checkout gives 0, 15 000, 12 000, so it is right only for the first order (int() cuts
#     the extra km). Receipt gives 15 000, 15 000, 15 000, right only for the third order and
#     only by luck (> instead of >=, and round(0.6) is 1). Courier gives 0, 15 600.0, 13 800.0,
#     right only for the first order, and it pays a float. For 90 000 / 4.2 km no service is
#     right. I checked it with print_old_results() (python task02.py).
#
# 2.2 Question: Use the Information Expert rule (slide 8): move the fee rule into the class
#     that has the data. The three services must call that one method instead of keeping their
#     own copies.
#     Answer: Order has food_total and distance_km, so the rule is now in Order.delivery_fee().
#     The three services only call order.delivery_fee(), so they can not be different anymore.
#
# 2.3 Question: The fee is money: it must be an int, never a float. Which function from the
#     math module gives you "every started kilometre"?
#     Answer: math.ceil(). ceil(1.2) == 2 and ceil(0.6) == 1, and it returns an int, so the
#     fee is always an int.
#
# 2.4 Question: Write tests for the boundaries: 149 999 and 150 000 sum; 3.0 km, 3.01 km and
#     4.0 km.
#     Answer: The tests are below (test_free_delivery_boundary, test_distance_boundary). All
#     numbers of the rule are constants in Order, so 3 000 -> 3 500 is a change of one line.
import math

import pytest


class Order:
    FREE_DELIVERY_FROM = 150_000   # sum
    BASE_FEE = 12_000              # sum, covers the first BASE_KM
    BASE_KM = 3
    FEE_PER_EXTRA_KM = 3_000       # sum for every started km after BASE_KM

    def __init__(self, food_total, distance_km):
        self.food_total = food_total
        self.distance_km = distance_km

    def delivery_fee(self) -> int:
        if self.food_total >= self.FREE_DELIVERY_FROM:
            return 0
        extra_km = math.ceil(max(0, self.distance_km - self.BASE_KM))
        return self.BASE_FEE + extra_km * self.FEE_PER_EXTRA_KM


class CheckoutService:
    def delivery_fee(self, order):
        return order.delivery_fee()


class ReceiptService:
    def delivery_fee(self, order):
        return order.delivery_fee()


class CourierPayoutService:
    def delivery_fee(self, order):
        return order.delivery_fee()


SERVICES = [CheckoutService(), ReceiptService(), CourierPayoutService()]


# old code of the three services, only for 2.1
def old_checkout_fee(order):
    if order.food_total >= 150_000:
        return 0
    extra = max(0, order.distance_km - 3)
    return 12_000 + int(extra) * 3_000


def old_receipt_fee(order):
    if order.food_total > 150_000:
        return 0
    extra = max(0, order.distance_km - 3)
    return 12_000 + round(extra) * 3_000


def old_courier_fee(order):
    if order.food_total >= 150_000:
        return 0
    return 12_000 + max(0, order.distance_km - 3) * 3_000


def print_old_results():
    for food_total, km in [(150_000, 4.2), (90_000, 4.2), (90_000, 3.6)]:
        order = Order(food_total, km)
        print(f"{food_total:>7} sum, {km} km: checkout={old_checkout_fee(order)}, "
              f"receipt={old_receipt_fee(order)}, courier={old_courier_fee(order)}, "
              f"rule={order.delivery_fee()}")


# tests
@pytest.mark.parametrize("food_total, km, expected", [
    (150_000, 4.2, 0),
    (90_000, 4.2, 18_000),
    (90_000, 3.6, 15_000),
])
def test_orders_from_2_1(food_total, km, expected):
    assert Order(food_total, km).delivery_fee() == expected


def test_old_services_disagreed():
    order = Order(90_000, 4.2)
    old_fees = {old_checkout_fee(order), old_receipt_fee(order), old_courier_fee(order)}
    assert old_fees == {15_000, 15_600}


@pytest.mark.parametrize("food_total, expected", [(149_999, 12_000), (150_000, 0)])
def test_free_delivery_boundary(food_total, expected):
    assert Order(food_total, 2.0).delivery_fee() == expected


@pytest.mark.parametrize("km, expected", [(3.0, 12_000), (3.01, 15_000), (4.0, 15_000)])
def test_distance_boundary(km, expected):
    assert Order(90_000, km).delivery_fee() == expected


@pytest.mark.parametrize("food_total, km", [
    (150_000, 4.2), (90_000, 4.2), (90_000, 3.6), (149_999, 3.01),
])
def test_all_services_agree_and_return_int(food_total, km):
    order = Order(food_total, km)
    fees = [service.delivery_fee(order) for service in SERVICES]
    assert fees == [order.delivery_fee()] * 3
    assert all(type(fee) is int for fee in fees)


def test_changing_the_price_per_km_is_one_line(monkeypatch):
    monkeypatch.setattr(Order, "FEE_PER_EXTRA_KM", 3_500)
    order = Order(90_000, 4.2)
    assert [service.delivery_fee(order) for service in SERVICES] == [19_000] * 3


if __name__ == "__main__":
    print_old_results()
