# Lab 4A. Extra task E5 - Appointments five hours late
# Student: Javohir Gayratov
#
# E5.1 Question: Write the invariant: in which form is starts_at kept inside the object?
#     Answer: starts_at is always an aware datetime in UTC inside the object. The time zone of
#     the user is used only when the time comes in and when it is shown.
#
# E5.2 Question: Reject naive datetimes in the constructor with ValueError.
#     Answer: The constructor raises ValueError if starts_at.tzinfo is None (or utcoffset() is
#     None). An aware time is converted with astimezone(timezone.utc).
#
# E5.3 Question: Add local_start(tz_name) that returns the start time in a given zone, for
#     example 'Asia/Tashkent'. Use zoneinfo (on Windows also run pip install tzdata).
#     Answer: local_start() converts the UTC time with zoneinfo.ZoneInfo(tz_name), so 09:00 in
#     Tashkent is stored as 04:00 UTC and shown again as 09:00.
#
# E5.4 Question: Add is_movable(now) for the 24-hour rule from Task 3. Why is now a parameter
#     and not datetime.now() inside the method?
#     Answer: is_movable(now) is True while the visit is at least 24 hours away. now is a
#     parameter so the tests can use fixed times and check the exact boundary. datetime.now()
#     inside would depend on the clock and the time zone of the server, and that is the same
#     mistake that caused this incident.
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pytest

TASHKENT = ZoneInfo("Asia/Tashkent")


def require_aware(value, name):
    if not isinstance(value, datetime):
        raise TypeError(f"{name} must be a datetime, got {value!r}")
    if value.tzinfo is None or value.utcoffset() is None:
        raise ValueError(f"{name} must have a time zone, got naive {value}")


class Appointment:
    FREE_MOVE_BEFORE = timedelta(hours=24)
    MOVE_FEE = 50_000   # sum

    def __init__(self, patient, starts_at):
        require_aware(starts_at, "starts_at")
        self.patient = patient
        self._starts_at = starts_at.astimezone(timezone.utc)

    @property
    def starts_at(self):
        return self._starts_at

    def local_start(self, tz_name):
        return self._starts_at.astimezone(ZoneInfo(tz_name))

    def is_movable(self, now):
        require_aware(now, "now")
        return self._starts_at - now >= self.FREE_MOVE_BEFORE

    def move_fee(self, now):
        return 0 if self.is_movable(now) else self.MOVE_FEE


def test_naive_datetime_is_rejected():
    with pytest.raises(ValueError):
        Appointment("Ali", datetime(2026, 11, 3, 9, 0))


def test_stored_in_utc_shown_in_tashkent():
    visit = Appointment("Ali", datetime(2026, 11, 3, 9, 0, tzinfo=TASHKENT))
    assert visit.starts_at == datetime(2026, 11, 3, 4, 0, tzinfo=timezone.utc)
    assert visit.starts_at.tzinfo is timezone.utc
    local = visit.local_start("Asia/Tashkent")
    assert (local.hour, local.minute) == (9, 0)


def test_the_same_moment_from_another_zone():
    visit = Appointment("Ali", datetime(2026, 11, 3, 4, 0, tzinfo=timezone.utc))
    assert visit.local_start("Asia/Tashkent").hour == 9


VISIT = Appointment("Ali", datetime(2026, 11, 3, 9, 0, tzinfo=TASHKENT))


@pytest.mark.parametrize("now, movable", [
    (datetime(2026, 11, 1, 12, 0, tzinfo=TASHKENT), True),     # 45 hours before
    (datetime(2026, 11, 2, 9, 0, tzinfo=TASHKENT), True),      # exactly 24 hours before
    (datetime(2026, 11, 2, 9, 1, tzinfo=TASHKENT), False),     # 23 h 59 min before
    (datetime(2026, 11, 2, 4, 0, tzinfo=timezone.utc), True),  # the same 24 h, given in UTC
    (datetime(2026, 11, 3, 10, 0, tzinfo=TASHKENT), False),    # the visit has started
])
def test_24_hour_rule(now, movable):
    assert VISIT.is_movable(now) is movable
    assert VISIT.move_fee(now) == (0 if movable else 50_000)


def test_now_must_be_aware_too():
    with pytest.raises(ValueError):
        VISIT.is_movable(datetime(2026, 11, 1, 12, 0))
