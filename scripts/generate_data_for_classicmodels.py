import pymysql.cursors
from faker import Faker

fake = Faker()
# Connect to the database
connection = pymysql.connect(host='localhost',
                             user='root',
                             password='root',
                             database='classicmodels',
                             cursorclass=pymysql.cursors.DictCursor)

with connection:
    with connection.cursor() as cursor:
        # Create a new record
        sql = "SELECT max(customerNumber) as max_customer_number FROM customers"
        cursor.execute(sql)
        max_id = cursor.fetchone()
        
        current_id = int(max_id["max_customer_number"]) + 1
        sql = """insert  into customers(
            customerNumber,customerName,contactLastName,contactFirstName,phone,addressLine1,addressLine2,city,state,postalCode,country,salesRepEmployeeNumber,creditLimit) 
            values  (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        data = []
        for i in range(1, 100000):
            current_id = current_id + 1
            print(current_id, i)
            data.append((current_id, fake.name(), fake.last_name(), fake.first_name(), fake.phone_number(), fake.street_address(), fake.street_address(), fake.city(), fake.state(), fake.postalcode(), fake.country_code(), 1188, 100000))
        cursor.executemany(sql, data)
        
    connection.commit()