import pymssql
import random
from faker import Faker
from datetime import datetime, timedelta

# LOCAL ENV
conn = pymssql.connect('localhost:1433', 'sa', 'root@@@123', "BikeStores")

# DOCKER ENV
# conn = pymssql.connect('mssql:1433', 'sa', 'root@@@123', "BikeStores")

cursor = conn.cursor(as_dict=True)
MAX_PRODUCT_PER_ORDER = 10
MAX_TIME_DELTA = 5
num_products = random.randint(1, MAX_PRODUCT_PER_ORDER)

# get random products
cursor.execute('SELECT product_id FROM products')
products = list(map(lambda row: row["product_id"], cursor))
random_products = random.sample(products, num_products)

# get random customer
cursor.execute('SELECT customer_id FROM customers')
customers = list(map(lambda row: row["customer_id"], cursor))
random_customer = random.sample(customers, 1)[0]

# get random store
cursor.execute('SELECT store_id FROM stores')
stores = list(map(lambda row: row["store_id"], cursor))
random_store = random.sample(stores, 1)[0]

# get random staff inside that store
cursor.execute(f'SELECT staff_id FROM staffs WHERE store_id = {random_store}')
staffs = list(map(lambda row: row["staff_id"], cursor))
random_staff = random.sample(staffs, 1)[0]

# get random order status
random_order_status = random.sample([1, 2, 3, 4], 1)[0]


# generate random date
def generate_date_in_range(start_date, end_date):
    faker = Faker()
    return faker.date_between_dates(date_start=start_date, date_end=end_date)

start_date = datetime(2018, 1, 1)  # Adjust these as needed
end_date = datetime(2024, 6, 23)  # Today's date for example

random_date = generate_date_in_range(start_date, end_date)

random_order_date = generate_date_in_range(start_date, end_date)
random_required_date_delta = random.randint(1, MAX_TIME_DELTA)
random_required_date = random_order_date + timedelta(days=random_required_date_delta)
random_shipped_date_delta = random.randint(1, MAX_TIME_DELTA) 
random_shipped_date = random_order_date + timedelta(days=random_shipped_date_delta)

print(random_customer, random_store, random_staff, random_order_status, random_order_date, random_required_date, random_shipped_date)

# insert random data
new_order = (random_customer, random_order_status, random_order_date, random_required_date, random_shipped_date, random_store, random_staff)
insert_query = """
    INSERT INTO orders(customer_id, order_status, order_date, required_date, shipped_date, store_id,staff_id)
    VALUES(%s, %s, %s, %s, %s, %s, %s)
"""

cursor.execute(insert_query, new_order)
conn.commit()
cursor.close()
conn.close()
