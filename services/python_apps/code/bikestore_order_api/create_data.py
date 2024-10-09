import pymssql
import random
from faker import Faker
from datetime import datetime, timedelta
import logging
logger = logging.getLogger('werkzeug')

MAX_PRODUCT_PER_ORDER = 10
MAX_QUANTITY_PER_ORDER_ITEM = 5
MAX_TIME_DELTA = 5

db_host = 'mssql:1433' 
db_user = 'sa'
db_pass = 'root@@@123' 
db_name = "BikeStores"


# generate random date
def generate_date_in_range(start_date, end_date):
    faker = Faker()
    return faker.date_between_dates(date_start=start_date, date_end=end_date)


def generate_order(customer, order_status, order_date: datetime, required_date: datetime, shipped_date: datetime, store, staff, products):
    conn = pymssql.connect(db_host, db_user, db_pass, db_name)
    cursor = conn.cursor(as_dict=True)
    new_order = (customer, order_status, order_date, required_date, shipped_date, store, staff)
    print("NEW ORDER:", new_order)
    
    insert_query = """
        INSERT INTO orders(customer_id, order_status, order_date, required_date, shipped_date, store_id, staff_id)
        VALUES(%s, %s, %s, %s, %s, %s, %s)
    """

    cursor.execute(insert_query, new_order)
    conn.commit()
    if order_date is not None:
        order_date = order_date.strftime("%Y-%m-%d %H:%M:%S")
        
    if shipped_date is not None:
        shipped_date = shipped_date.strftime("%Y-%m-%d %H:%M:%S")
        
    if required_date is not None:
        required_date = required_date.strftime("%Y-%m-%d %H:%M:%S")
        
    cursor.execute(f"""
        SELECT top 1 * FROM orders 
        WHERE 1=1 
            AND customer_id = {customer}
            AND order_status = {order_status}
            AND store_id = {store}
            AND staff_id = {staff}
            AND order_date = '{order_date}'
        order by updated_at desc
    """)
    new_order = cursor.fetchone()
    logger.info("NEW ORDER", new_order, "TEST")
    new_order_id = new_order["order_id"]
    new_order_items = []
    for i, product in enumerate(products):
        random_product_id = int(product["product_id"])
        cursor.execute(f"SELECT list_price FROM products WHERE product_id = {random_product_id}")
        list_price = (cursor.fetchone())["list_price"]
        logger.info("list price", list_price, random_product_id)
        new_order_item = (new_order_id, i + 1, random_product_id, random.randint(1, MAX_QUANTITY_PER_ORDER_ITEM), list_price, 0)
        new_order_items.append(new_order_item)
        insert_query = """
            INSERT INTO order_items(order_id, item_id, product_id, quantity, list_price, discount)
            VALUES(%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, new_order_item)
        conn.commit()
        print("NEW ORDER ITEM", i + 1, new_order_item)
    cursor.close()
    conn.close()
    
    return {
        "order": new_order,
        "order_items": new_order_items
    }


def generate_random_order():
    # LOCAL ENV
    conn = pymssql.connect(db_host, db_user, db_pass, db_name)

    # DOCKER ENV
    # conn = pymssql.connect('mssql:1433', 'sa', 'root@@@123', "BikeStores")

    cursor = conn.cursor(as_dict=True)
    
    num_products = random.randint(1, MAX_PRODUCT_PER_ORDER)

    # get random products
    cursor.execute('SELECT product_id, list_price FROM products')
    products = list(map(lambda row: {"product_id": row["product_id"], "list_price": row["list_price"]}, cursor))
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

    start_date = datetime(2018, 1, 1)  # Adjust these as needed
    end_date = datetime(2024, 6, 23)  # Today's date for example

    random_order_date = generate_date_in_range(start_date, end_date)
    random_required_date_delta = random.randint(1, MAX_TIME_DELTA)
    random_required_date = random_order_date + timedelta(days=random_required_date_delta)
    random_shipped_date_delta = random.randint(1, MAX_TIME_DELTA) 
    random_shipped_date = random_order_date + timedelta(days=random_shipped_date_delta)

    print(random_customer, random_store, random_staff, random_order_status, random_order_date, random_required_date, random_shipped_date)
    return generate_order(random_customer, random_order_status, random_order_date, random_required_date, random_shipped_date, random_store, random_staff, random_products)

    