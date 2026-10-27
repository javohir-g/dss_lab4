# Lab 4A. Task 8 - Somebody changed my order
# Student: Javohir Gayratov
#
# 8.1 Question: Explain both causes. Use the words composition and aliasing (two names for the
#     same object).
#     Answer: (a) Aliasing: Order keeps the same list object that the cart gave it, so
#     cart_lines and order.lines are two names for one list, and cart_lines.append() also
#     changes the confirmed order. (b) Order gives out its own list, so the promo module can
#     append to it and skip confirm(). Both break composition: the lines are parts that only
#     the Order should own and change, but other objects hold them and change them.
#
# 8.2 Question: Order owns its lines (composition). Copy what the constructor receives, and
#     give the outside world only a read-only view of the lines.
#     Answer: The constructor puts every line into a new private list (through add_line), and
#     lines returns a tuple, a read-only copy. The lines are tuples too, so one line also can
#     not be changed from outside.
#
# 8.3 Question: Add add_line(sku, qty, unit_price). It rejects qty < 1, and it rejects any
#     change after confirm() by raising your own OrderLockedError.
#     Answer: add_line() first checks the status and raises OrderLockedError after confirm().
#     qty must be an int >= 1 and unit_price an int >= 0, otherwise ValueError or TypeError.
#
# 8.4 Question: New invariant: an order with no lines cannot be confirmed. Which method checks
#     it?
#     Answer: confirm(). The rule is about the step draft -> confirmed, and Order has both the
#     lines and the status, so confirm() raises EmptyOrderError.
import pytest


class OrderLockedError(Exception):
    pass


class EmptyOrderError(Exception):
    pass


class Order:
    def __init__(self, order_id, lines=()):
        self._order_id = order_id
        self._lines = []
        self._status = "draft"
        for sku, qty, unit_price in lines:
            self.add_line(sku, qty, unit_price)

    @property
    def order_id(self):
        return self._order_id

    @property
    def status(self):
        return self._status

    @property
    def lines(self):
        return tuple(self._lines)

    def add_line(self, sku, qty, unit_price):
        if self._status != "draft":
            raise OrderLockedError(f"order {self._order_id} is {self._status}, it cannot change")
        for name, value in (("qty", qty), ("unit_price", unit_price)):
            if isinstance(value, bool) or not isinstance(value, int):
                raise TypeError(f"{name} must be an int, got {value!r}")
        if qty < 1:
            raise ValueError(f"qty must be at least 1, got {qty}")
        if unit_price < 0:
            raise ValueError(f"unit_price cannot be negative, got {unit_price}")
        self._lines.append((sku, qty, unit_price))

    def total(self):
        return sum(qty * price for _, qty, price in self._lines)

    def confirm(self):
        if self._status != "draft":
            raise OrderLockedError(f"order {self._order_id} is already {self._status}")
        if not self._lines:
            raise EmptyOrderError(f"order {self._order_id} has no lines")
        self._status = "confirmed"


def run_bug_report_script():
    cart_lines = [("A1", 2, 50_000)]
    order = Order(1001, cart_lines)
    order.confirm()
    cart_lines.append(("B7", 1, 30_000))   # the cart keeps working
    return order.total()


def test_script_prints_100000():
    assert run_bug_report_script() == 100_000


def test_lines_cannot_be_appended_from_outside():
    order = Order(1001, [("A1", 2, 50_000)])
    with pytest.raises(AttributeError):
        order.lines.append(("PROMO", 1, -10_000))
    with pytest.raises(AttributeError):
        order.lines = []
    assert order.total() == 100_000


def test_add_line_before_and_after_confirm():
    order = Order(1001)
    order.add_line("A1", 2, 50_000)
    order.add_line("B7", 1, 30_000)
    assert order.total() == 130_000
    order.confirm()
    with pytest.raises(OrderLockedError):
        order.add_line("PROMO", 1, 0)
    assert order.total() == 130_000


@pytest.mark.parametrize("qty", [0, -3])
def test_qty_below_one_is_rejected(qty):
    order = Order(1001)
    with pytest.raises(ValueError):
        order.add_line("A1", qty, 50_000)
    assert order.lines == ()


def test_constructor_validates_lines_too():
    with pytest.raises(ValueError):
        Order(1001, [("A1", 0, 50_000)])


def test_empty_order_cannot_be_confirmed():
    order = Order(1001)
    with pytest.raises(EmptyOrderError):
        order.confirm()
    assert order.status == "draft"


def test_confirm_twice_is_an_error():
    order = Order(1001, [("A1", 1, 50_000)])
    order.confirm()
    with pytest.raises(OrderLockedError):
        order.confirm()


if __name__ == "__main__":
    print(run_bug_report_script())
