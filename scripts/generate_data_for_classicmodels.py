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
        sql = """insert  into customers(
            customerName,contactLastName,contactFirstName,phone,addressLine1,addressLine2,city,state,postalCode,country,salesRepEmployeeNumber,creditLimit) 
            values  (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        data = []
        for i in range(0, 10000):
            print(i)
            data.append((fake.name(), fake.last_name(), fake.first_name(), fake.phone_number(), fake.street_address(), fake.street_address(), fake.city(), fake.state(), fake.postalcode(), fake.country_code(), 1188, 100000))
        cursor.executemany(sql, data)
        
    connection.commit()