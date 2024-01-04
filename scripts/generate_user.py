import mysql.connector
from random import randint, choice
from faker import Faker

# Install the Faker library if not already installed
# pip install faker

MAX_NUM_USER = 1000

# MySQL connection parameters
db_config = {
    'host': 'localhost',
    'user': 'root',
    'password': 'root',
    'database': 'test',
}

# Connect to MySQL
connection = mysql.connector.connect(**db_config)
cursor = connection.cursor()


# Function to generate random data using Faker
def generate_random_data():
    fake = Faker()
    return {
        'name': fake.name(),
        'email': fake.email(),
        'age': randint(18, 65),
        'city': fake.city(),
        'country': fake.country(),
    }


# Get the count of test.user table
count_query = "SELECT COUNT(*) FROM test.user"
cursor.execute(count_query)
count = cursor.fetchone()[0]
print("Count of test.user table:", count)

if count < MAX_NUM_USER:
    # BEGIN: be15d9bcejpp
    # Create table if not exists
    create_table_query = """
    CREATE TABLE IF NOT EXISTS test.user (
        id INT AUTO_INCREMENT PRIMARY KEY,
        name VARCHAR(255),
        email VARCHAR(255),
        age INT,
        city VARCHAR(255),
        country VARCHAR(255)
    )
    """
    cursor.execute(create_table_query)
    connection.commit()

    # Insert 1000 records into the table
    for _ in range(MAX_NUM_USER):
        data = generate_random_data()
        insert_query = """
        INSERT INTO test.user (name, email, age, city, country)
        VALUES (%s, %s, %s, %s, %s)
        """
        cursor.execute(insert_query, (data['name'], data['email'], data['age'], data['city'], data['country']))

    # Commit the changes and close the connection
    connection.commit()
    connection.close()

    print(f"Inserted {MAX_NUM_USER} records successfully.")
else:
    print(f"Count is already greater than or equal to {MAX_NUM_USER}. No action needed.")