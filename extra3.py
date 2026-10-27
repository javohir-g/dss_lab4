# Lab 4A. Extra task E3 - One seat, two tickets
# Student: Javohir Gayratov
#
# E3.1 Question: Which class must enforce the rule? Answer with "who has the data": who knows
#     all the tickets of one session?
#     Answer: Session. A Seat does not know about tickets and a Ticket knows only itself, but
#     the Session knows all tickets sold for this showing, so it has the data.
#
# E3.2 Question: Implement Session.book(seat, customer). It returns a Ticket, or raises
#     SeatTakenError if the seat is already sold.
#     Answer: book() checks that the seat exists in the hall and is still free, then creates
#     and saves the Ticket. A sold seat raises SeatTakenError. The tickets are private and are
#     given out only as a read-only view.
#
# E3.3 Question: Write a test for double booking.
#     Answer: test_double_booking_raises_seat_taken below.
#
# E3.4 Question: Production runs 4 API servers, and each server loads its own Session objects
#     from the database. Is your check still enough? What must the database add?
#     Answer: No. Every server has its own Session object, so two requests on two servers can
#     both see the seat as free and both sell it. The database must add a UNIQUE constraint on
#     tickets(session_id, seat_id): then the second INSERT fails and we turn this error into
#     SeatTakenError. (SELECT ... FOR UPDATE also works, but a unique constraint can not be
#     forgotten in some part of the code.)
from dataclasses import dataclass
from types import MappingProxyType

import pytest


class SeatTakenError(Exception):
    pass


@dataclass(frozen=True)
class Ticket:
    session_id: int
    seat: str
    customer: str


class Session:
    def __init__(self, session_id, film, seats):
        self._session_id = session_id
        self.film = film
        self._seats = frozenset(seats)
        self._tickets = {}       # seat -> Ticket, at most one per seat

    @property
    def tickets(self):
        return MappingProxyType(self._tickets)

    def is_free(self, seat):
        return seat in self._seats and seat not in self._tickets

    def book(self, seat, customer):
        if seat not in self._seats:
            raise ValueError(f"there is no seat {seat!r} in this hall")
        if seat in self._tickets:
            raise SeatTakenError(f"seat {seat} is already sold for session {self._session_id}")
        ticket = Ticket(self._session_id, seat, customer)
        self._tickets[seat] = ticket
        return ticket


def make_session():
    return Session(501, "Dune", ["A1", "A2", "A3"])


def test_book_returns_ticket():
    session = make_session()
    ticket = session.book("A1", "Ali")
    assert ticket == Ticket(501, "A1", "Ali")
    assert not session.is_free("A1") and session.is_free("A2")


def test_double_booking_raises_seat_taken():
    session = make_session()
    session.book("A1", "Ali")
    with pytest.raises(SeatTakenError):
        session.book("A1", "Vali")
    assert session.tickets["A1"].customer == "Ali"
    assert len(session.tickets) == 1


def test_unknown_seat_is_rejected():
    with pytest.raises(ValueError):
        make_session().book("Z9", "Ali")


def test_tickets_cannot_be_added_from_outside():
    session = make_session()
    with pytest.raises(TypeError):
        session.tickets["A2"] = Ticket(501, "A2", "Vali")
