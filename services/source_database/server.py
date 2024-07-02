from flask import Flask
import pymssql
import random
from faker import Faker
from datetime import datetime, timedelta
from create_data import generate_random_order
from flask import request

app = Flask("hello")

@app.route("/", methods=["POST"])
def generate_order():
    print("request", request.method)
    customer_id = request.args.get("customer_id")
    staff_id = request.args.get("staff_id")
    store_id = request.args.get("store_id")
    product_id = request.args.get("product_id")
    new_order_status = 1
    order_date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    required_date = None
    shipped_date = None
    return generate_order()