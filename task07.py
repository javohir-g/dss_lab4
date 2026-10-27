# Lab 4A. Task 7 - The class design decides what happens on delete (on paper)
# Student: Javohir Gayratov
#
# 7.1 Question: Find every pair of connected classes and name the relationship: dependency,
#     association, aggregation or composition (slides 25-27).
#     Answer:
#     - Order - Customer: association. Order keeps self.customer, but the customer is created
#       outside and lives without the order.
#     - Order - OrderLine: composition. Order creates every OrderLine itself in add() and keeps
#       it in self.lines; nobody else has the line and it means nothing without the order.
#     - OrderLine - Product: association. The line keeps a product that lives in the catalog.
#     - Order - Courier: association (optional). self.courier is set later by assign(), and the
#       courier lives on its own.
#     - Catalog - Product: aggregation. Catalog keeps a list of products, but they are created
#       outside and passed in, so they live without the catalog.
#     - Order -> Product: dependency. add() uses product only as a parameter to read the price
#       (the reference that stays goes through OrderLine).
#     - SmsGateway -> Order: dependency. order is only a parameter of order_shipped().
#     Diagram (<*> composition, <> aggregation):
#         Customer 1 ------- 0..* Order 1 <*>------ 0..* OrderLine 0..* ------- 1 Product
#                                 0..*                                         0..*
#                                  |                                            |
#                                 0..1                                         0..*
#                                Courier                                    <> Catalog
#
# 7.2 Question: Give the multiplicity at both ends of each relationship (slide 28). Which
#     multiplicity is not enforced by the code yet?
#     Answer:
#     - Order - Customer: an order has exactly 1 customer, a customer has 0..* orders.
#     - Order - OrderLine: an order has 0..* lines (1..* when it is placed), a line belongs to
#       exactly 1 order.
#     - OrderLine - Product: a line has exactly 1 product, a product is in 0..* lines.
#     - Order - Courier: an order has 0..1 courier, a courier has 0..* orders.
#     - Catalog - Product: a catalog has 0..* products, a product is in 0..* catalogs.
#     Not enforced yet: "exactly 1 customer" (Order(None) works, the same for a line with
#     product None) and "1..* lines for a placed order" (the code never checks that an order
#     has lines, and qty >= 1 is not checked either).
#
# 7.3 Question: Choose ON DELETE for each of these foreign keys and justify it with the
#     relationship: order_lines.order_id, order_lines.product_id, orders.customer_id,
#     orders.courier_id.
#     Answer: I used the lifetime test: does the part disappear with the whole?
#     - order_lines.order_id: CASCADE. Composition: the lines are parts of the order and
#       disappear with it.
#     - order_lines.product_id: RESTRICT. Association: the line must still show what was sold.
#       A product that was sold once is archived (is_active = false), not deleted.
#     - orders.customer_id: RESTRICT. Association with exactly 1, so the column is NOT NULL and
#       SET NULL is impossible. Orders are money records and must stay; if a customer wants
#       their data deleted, we anonymise the customer row instead.
#     - orders.courier_id: SET NULL. Association with 0..1: the order stays when a courier is
#       removed, and "no courier" is a normal state of an order. (For delivered orders it is
#       better to deactivate the courier than to delete the row, so we still know who
#       delivered.)
#
# 7.4 Question: OrderLine stores unit_price although Product already has price. Why is this
#     copy correct in production and not a DRY violation?
#     Answer: unit_price is the price at the moment of the sale. It is a different fact from
#     Product.price, which is today's catalog price. When the price changes tomorrow, the total
#     of an old order, its receipt and refunds must stay the same. DRY means one piece of
#     knowledge in one place, but here we have two different facts that are only equal when
#     the order is created, so the copy is correct.


# the code from the task, with the relationships written next to the fields

class Customer:
    def __init__(self, name, phone):
        self.name, self.phone = name, phone


class Product:
    def __init__(self, sku, title, price):
        self.sku, self.title, self.price = sku, title, price


class OrderLine:
    def __init__(self, product, qty, unit_price):
        self.product = product          # association, exactly 1 product
        self.qty = qty
        self.unit_price = unit_price    # price at the moment of the sale (7.4)


class Courier:
    def __init__(self, name):
        self.name = name


class Order:
    def __init__(self, customer):
        self.customer = customer        # association, exactly 1 customer
        self.lines = []                 # composition, 0..* lines
        self.courier = None             # association, 0..1 courier

    def add(self, product, qty):        # dependency on Product (only a parameter)
        self.lines.append(OrderLine(product, qty, product.price))

    def assign(self, courier):
        self.courier = courier


class Catalog:
    def __init__(self, products):
        self.products = list(products)  # aggregation, 0..* products


class SmsGateway:
    def order_shipped(self, order):     # dependency on Order (only a parameter)
        ...
