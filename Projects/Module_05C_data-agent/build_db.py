"""Architecture & Agents starter — build the sample database.

Deterministically generates a small e-commerce dataset into `data.db`
(SQLite). Run once:

    python build_db.py

Same seed → identical data every time, so everyone's answers match.
A prebuilt `data.db` already ships with the project; rerun this only
if you want to change or regrow the data.

Schema
------
    customers(id, name, email, country, signup_date)
    products(id, name, category, price, cost)
    orders(id, customer_id, order_date, status)
    order_items(id, order_id, product_id, quantity, unit_price)
"""
import os
import random
import sqlite3
from datetime import date, timedelta

DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")
SEED = 42

# The data spans ~18 months ending on a fixed anchor date. Time-relative
# questions ("last quarter") are meant to be worked out from the most recent
# order_date in the data, NOT from the wall clock — so the dataset stays valid
# no matter when a student runs it.
END_DATE = date(2026, 5, 31)
START_DATE = END_DATE - timedelta(days=545)  # ~18 months

N_CUSTOMERS = 500
N_ORDERS = 3000

COUNTRIES = ["USA", "USA", "USA", "Canada", "UK", "Germany",
             "France", "Australia", "Japan", "Brazil"]  # weighted toward USA

FIRST = ["Ava", "Liam", "Mia", "Noah", "Emma", "Oliver", "Sophia", "Lucas",
         "Isabella", "Mason", "Amelia", "Ethan", "Harper", "James", "Charlotte",
         "Benjamin", "Yuki", "Hana", "Diego", "Lucia", "Anika", "Omar"]
LAST = ["Smith", "Johnson", "Williams", "Brown", "Garcia", "Miller", "Davis",
        "Rodriguez", "Martinez", "Tanaka", "Sato", "Mueller", "Dubois", "Silva",
        "Costa", "Khan", "Nguyen", "Kim", "Rossi", "Andersen"]

# category -> (list of product names, (price_low, price_high))
CATALOG = {
    "Electronics": (["Wireless Earbuds", "Bluetooth Speaker", "4K Monitor",
                     "Mechanical Keyboard", "USB-C Hub", "HD Webcam",
                     "Noise-Cancelling Headphones", "Portable SSD",
                     "Smart Plug", "Gaming Mouse"], (25, 320)),
    "Home": (["Coffee Maker", "Air Fryer", "Robot Vacuum", "Table Lamp",
              "Throw Blanket", "Cookware Set", "Standing Desk", "Office Chair",
              "Water Filter", "Scented Candle"], (15, 420)),
    "Books": (["The Pragmatic Programmer", "Designing Data-Intensive Apps",
               "Clean Code", "Sapiens", "Atomic Habits", "Dune",
               "Project Hail Mary", "The Midnight Library", "Educated",
               "Thinking, Fast and Slow"], (10, 32)),
    "Toys": (["Building Blocks Set", "RC Car", "Plush Bear", "1000-pc Puzzle",
              "Board Game", "Art Kit", "Wooden Train", "Action Figure",
              "Dollhouse", "Science Kit"], (10, 70)),
    "Clothing": (["Cotton T-Shirt", "Hoodie", "Running Shoes", "Denim Jeans",
                  "Wool Socks", "Rain Jacket", "Baseball Cap", "Yoga Pants",
                  "Flannel Shirt", "Leather Belt"], (12, 130)),
    "Sports": (["Yoga Mat", "Dumbbell Set", "Tennis Racket", "Soccer Ball",
                "Resistance Bands", "Water Bottle", "Bike Helmet",
                "Camping Tent", "Hiking Backpack", "Jump Rope"], (8, 210)),
}

# Orders are weighted toward "completed"; the rest exercise status filtering.
STATUS = ["completed"] * 80 + ["cancelled"] * 12 + ["refunded"] * 8


def rand_date(lo: date, hi: date) -> date:
    return lo + timedelta(days=random.randint(0, (hi - lo).days))


def main() -> None:
    random.seed(SEED)
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.executescript(
        """
        CREATE TABLE customers (
            id          INTEGER PRIMARY KEY,
            name        TEXT NOT NULL,
            email       TEXT NOT NULL,
            country     TEXT,
            signup_date TEXT NOT NULL
        );
        CREATE TABLE products (
            id       INTEGER PRIMARY KEY,
            name     TEXT NOT NULL,
            category TEXT NOT NULL,
            price    REAL NOT NULL,
            cost     REAL NOT NULL
        );
        CREATE TABLE orders (
            id          INTEGER PRIMARY KEY,
            customer_id INTEGER NOT NULL REFERENCES customers(id),
            order_date  TEXT NOT NULL,
            status      TEXT NOT NULL
        );
        CREATE TABLE order_items (
            id         INTEGER PRIMARY KEY,
            order_id   INTEGER NOT NULL REFERENCES orders(id),
            product_id INTEGER NOT NULL REFERENCES products(id),
            quantity   INTEGER NOT NULL,
            unit_price REAL NOT NULL
        );
        """
    )

    # ---- products ----
    products = []  # (id, price)
    pid = 1
    for category, (names, (lo, hi)) in CATALOG.items():
        for name in names:
            price = round(random.uniform(lo, hi), 2)
            cost = round(price * random.uniform(0.45, 0.70), 2)
            cur.execute(
                "INSERT INTO products (id, name, category, price, cost) VALUES (?,?,?,?,?)",
                (pid, name, category, price, cost),
            )
            products.append((pid, price))
            pid += 1

    # ---- customers ----
    customers = []  # (id, signup_date)
    for cid in range(1, N_CUSTOMERS + 1):
        first, last = random.choice(FIRST), random.choice(LAST)
        email = f"{first.lower()}.{last.lower()}{cid}@example.com"
        country = random.choice(COUNTRIES)
        if random.random() < 0.05:
            country = None  # a few missing countries — real data has gaps
        signup = rand_date(START_DATE - timedelta(days=365), END_DATE)
        cur.execute(
            "INSERT INTO customers (id, name, email, country, signup_date) VALUES (?,?,?,?,?)",
            (cid, f"{first} {last}", email, country, signup.isoformat()),
        )
        customers.append((cid, signup))

    # ---- orders + order_items ----
    item_id = 1
    for oid in range(1, N_ORDERS + 1):
        cid, signup = random.choice(customers)
        earliest = max(START_DATE, signup)
        order_date = rand_date(earliest, END_DATE)
        status = random.choice(STATUS)
        cur.execute(
            "INSERT INTO orders (id, customer_id, order_date, status) VALUES (?,?,?,?)",
            (oid, cid, order_date.isoformat(), status),
        )
        for pid, price in random.sample(products, random.randint(1, 5)):
            qty = random.randint(1, 4)
            unit_price = round(price * 0.9, 2) if random.random() < 0.10 else price
            cur.execute(
                "INSERT INTO order_items (id, order_id, product_id, quantity, unit_price) "
                "VALUES (?,?,?,?,?)",
                (item_id, oid, pid, qty, unit_price),
            )
            item_id += 1

    conn.commit()

    counts = {
        t: cur.execute(f"SELECT COUNT(*) FROM {t}").fetchone()[0]
        for t in ("customers", "products", "orders", "order_items")
    }
    conn.close()
    print(f"Wrote {DB_PATH}")
    for t, n in counts.items():
        print(f"  {t:12} {n:>6}")


if __name__ == "__main__":
    main()
