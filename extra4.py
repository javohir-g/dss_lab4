# Lab 4A. Extra task E4 - The lost phone number
# Student: Javohir Gayratov
#
# E4.1 Question: Reproduce it: load customer 42 twice, change the phone on the first object and
#     save it, then save the second object. Show that the change is lost.
#     Answer: test_lost_update_with_old_repository: both screens get their own Customer object
#     for id 42. The first one saves the new phone, then the second one saves its old copy over
#     it, and the new phone is lost without any error.
#
# E4.2 Question: Add an identity map to the repository: inside one repository, get(42) always
#     returns the same Customer object. Check it with is.
#     Answer: The repository keeps a dict customer_id -> Customer. get(42) creates the object
#     only the first time and then always returns the same one, so both screens change one
#     object and the second save writes the new phone, not the old one.
#
# E4.3 Question: Is the relationship between the repository and the customers it returns
#     aggregation or composition? Use the lifetime test.
#     Answer: Aggregation. The customers do not disappear with the repository: their rows stay
#     in the database, and screens can still use the objects after the repository is gone.
#
# E4.4 Question: The identity map does not help when two different servers change the same
#     customer. Name a technique that does. Hint: a version number on every row.
#     Answer: Optimistic locking. Every row has a version number and the update is
#     UPDATE ... SET ..., version = version + 1 WHERE id = 42 AND version = 7. If another server
#     saved first, 0 rows are updated, and we raise a conflict error instead of writing over
#     the other change.


class Customer:
    def __init__(self, customer_id, name, phone):
        self.customer_id, self.name, self.phone = customer_id, name, phone


class OldCustomerRepository:
    def __init__(self, rows):
        self._rows = rows

    def get(self, customer_id):
        row = self._rows[customer_id]
        return Customer(customer_id, row["name"], row["phone"])

    def save(self, customer):
        self._rows[customer.customer_id] = {"name": customer.name, "phone": customer.phone}


class CustomerRepository:
    def __init__(self, rows):
        self._rows = rows             # stands in for the database: id -> dict
        self._identity_map = {}       # id -> the one Customer object for this id

    def get(self, customer_id):
        if customer_id not in self._identity_map:
            row = self._rows[customer_id]
            self._identity_map[customer_id] = Customer(customer_id, row["name"], row["phone"])
        return self._identity_map[customer_id]

    def save(self, customer):
        self._identity_map[customer.customer_id] = customer
        self._rows[customer.customer_id] = {"name": customer.name, "phone": customer.phone}


def make_rows():
    return {42: {"name": "Dilnoza Karimova", "phone": "+998901234567"}}


def test_lost_update_with_old_repository():
    rows = make_rows()
    repo = OldCustomerRepository(rows)
    screen_1 = repo.get(42)
    screen_2 = repo.get(42)            # opened earlier, still has the old number
    screen_1.phone = "+998977654321"
    repo.save(screen_1)
    repo.save(screen_2)
    assert rows[42]["phone"] == "+998901234567"     # the change is lost


def test_identity_map_returns_the_same_object():
    repo = CustomerRepository(make_rows())
    assert repo.get(42) is repo.get(42)


def test_no_lost_update_with_identity_map():
    rows = make_rows()
    repo = CustomerRepository(rows)
    screen_1 = repo.get(42)
    screen_2 = repo.get(42)
    screen_1.phone = "+998977654321"
    repo.save(screen_1)
    repo.save(screen_2)
    assert rows[42]["phone"] == "+998977654321"
