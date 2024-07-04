from flask import Flask
import pymssql
import random
from faker import Faker
from datetime import datetime, timedelta
from create_data import generate_random_order, generate_order
from flask import request
from flask_cors import CORS, cross_origin
import sys

import logging
logger = logging.getLogger('werkzeug')

app = Flask("hello")
cors = CORS(app)

@app.route("/order", methods=["POST"])
@cross_origin()
def post_generate_order():
    print("request", request.method)
    customer_id = request.args.get("customer_id")
    staff_id = request.args.get("staff_id")
    store_id = request.args.get("store_id")
    product_id_param = request.args.get("product_id")
    product_id = []
    product_id.append({"product_id": product_id_param})
    print("debug", product_id,  file=sys.stdout)
    logger.info("debug", product_id)
    new_order_status = 1
    order_date = datetime.now()
    random_required_date = datetime.now() + timedelta(days=3)
    shipped_date = None
    print(order_date)
    return generate_order(customer_id, new_order_status, order_date, random_required_date, shipped_date, store_id, staff_id, product_id)