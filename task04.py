# Lab 4A. Task 4 - The negative balance in production
# Student: Javohir Gayratov
#
# 4.1 Question: Write the class so that the three rules always hold. amount must be a positive
#     int; anything else is rejected. Do you raise TypeError or ValueError for 10.5? For -10?
#     Note that isinstance(True, int) is True in Python: does your code accept deposit(True)?
#     Answer: 10.5 has the wrong type, so TypeError. -10 has the right type but a wrong value,
#     so ValueError. Because isinstance(True, int) is True, a simple isinstance check would
#     accept deposit(True) as 1 tiyin. My check rejects bool first, so it raises TypeError.
#
# 4.2 Question: balance and history are read-only from outside: wallet.history.append(...) and
#     wallet.history[0] = ... must not work.
#     Answer: The data is in _balance and _history. balance and history are properties without
#     a setter, and history returns a tuple (a copy), so .append() and [0] = ... do not work,
#     and wallet.balance -= 500 raises AttributeError.
#
# 4.3 Question: Add refund(amount). Is a refund a deposit, a withdrawal or a third kind of
#     entry? Why does the history care about the difference?
#     Answer: A third kind. It adds money like a deposit, but it is money returned for an old
#     payment, not new money from the user. Accounting, reports and fraud checks must see the
#     difference, and the wallet must not refund more than was withdrawn.
#
# 4.4 Question: Show in one line of Python why float is wrong for money (try 0.1 + 0.2), and
#     explain why an int in tiyin does not have this problem.
#     Answer: print(0.1 + 0.2 == 0.3) prints False (0.1 + 0.2 = 0.30000000000000004). float is
#     binary and can not store 0.1 exactly, so small errors add up. 10 + 20 == 30 tiyin is
#     exact, because int in Python has no rounding.
import pytest


class InsufficientFundsError(Exception):
    pass


# rules: balance is an int in tiyin and never < 0, only deposit/withdraw/refund change it,
# every change goes to history as (kind, amount, balance_after)
class Wallet:

    def __init__(self, owner_id):
        self._owner_id = owner_id
        self._balance = 0
        self._history = []

    @property
    def owner_id(self):
        return self._owner_id

    @property
    def balance(self):
        return self._balance

    @property
    def history(self):
        return tuple(self._history)

    def deposit(self, amount):
        self._check_amount(amount)
        self._change(+amount, "deposit", amount)

    def withdraw(self, amount):
        self._check_amount(amount)
        if amount > self._balance:
            raise InsufficientFundsError(f"balance is {self._balance}, cannot withdraw {amount}")
        self._change(-amount, "withdraw", amount)

    def refund(self, amount):
        self._check_amount(amount)
        if amount > self._refundable():
            raise ValueError(f"only {self._refundable()} tiyin can be refunded")
        self._change(+amount, "refund", amount)

    def _refundable(self):
        withdrawn = sum(amount for kind, amount, _ in self._history if kind == "withdraw")
        refunded = sum(amount for kind, amount, _ in self._history if kind == "refund")
        return withdrawn - refunded

    def _change(self, delta, kind, amount):
        self._balance += delta
        self._history.append((kind, amount, self._balance))

    @staticmethod
    def _check_amount(amount):
        if isinstance(amount, bool) or not isinstance(amount, int):
            raise TypeError(f"amount must be an int in tiyin, got {amount!r}")
        if amount <= 0:
            raise ValueError(f"amount must be positive, got {amount}")


def test_deposit_and_withdraw_write_history():
    wallet = Wallet("u1")
    wallet.deposit(10_000)
    wallet.withdraw(2_500)
    assert wallet.balance == 7_500
    assert wallet.history == (("deposit", 10_000, 10_000), ("withdraw", 2_500, 7_500))


def test_admin_script_line_raises_attribute_error():
    wallet = Wallet("u1")
    wallet.deposit(1_000)
    with pytest.raises(AttributeError):
        wallet.balance -= 500
    assert wallet.balance == 1_000


def test_cannot_go_below_zero():
    wallet = Wallet("u1")
    wallet.deposit(300)
    with pytest.raises(InsufficientFundsError):
        wallet.withdraw(301)
    wallet.withdraw(300)
    assert wallet.balance == 0
    with pytest.raises(InsufficientFundsError):
        wallet.withdraw(1)
    assert wallet.balance == 0 and len(wallet.history) == 2


@pytest.mark.parametrize("amount, error", [
    (10.5, TypeError), ("100", TypeError), (True, TypeError), (None, TypeError),
    (-10, ValueError), (0, ValueError),
])
def test_bad_amounts_are_rejected(amount, error):
    wallet = Wallet("u1")
    wallet.deposit(1_000)
    for method in (wallet.deposit, wallet.withdraw, wallet.refund):
        with pytest.raises(error):
            method(amount)
    assert wallet.balance == 1_000 and len(wallet.history) == 1


def test_history_cannot_be_changed_from_outside():
    wallet = Wallet("u1")
    wallet.deposit(500)
    with pytest.raises(AttributeError):
        wallet.history.append(("deposit", 1, 1))
    with pytest.raises(TypeError):
        wallet.history[0] = ("deposit", 999_999, 999_999)
    with pytest.raises(AttributeError):
        wallet.history = []
    assert wallet.history == (("deposit", 500, 500),)


def test_refund_is_its_own_kind_and_is_limited():
    wallet = Wallet("u1")
    wallet.deposit(5_000)
    wallet.withdraw(3_000)
    wallet.refund(1_000)
    assert wallet.history[-1] == ("refund", 1_000, 3_000)
    with pytest.raises(ValueError):
        wallet.refund(2_001)
    wallet.refund(2_000)
    assert wallet.balance == 5_000


def test_float_is_wrong_for_money():
    assert 0.1 + 0.2 != 0.3
    assert 10 + 20 == 30            # the same amounts in tiyin
