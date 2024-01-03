import mysql.connector
from random import randint, choice
from faker import Faker

# Install the Faker library if not already installed
# pip install faker

MAX_NUM_USER = 1000
MAX_NUM_INVENTORY = 3000
MAX_ID_RANGE = 1000
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
        'userid': randint(1, MAX_NUM_USER),
        'name': fake.name(),
        'created_date': fake.date_time_this_decade(),
        'modified_date': fake.date_time_this_decade(),
    }


# Create table if not exists
create_table_query = """
    CREATE TABLE IF NOT EXISTS test.inventory (
        id INT AUTO_INCREMENT PRIMARY KEY,
        userid INT,
        name VARCHAR(255),
        created_date DATETIME,
        modified_date DATETIME
    )
"""
cursor.execute(create_table_query)
connection.commit()

# Insert 1000 records into the table
for _ in range(MAX_NUM_INVENTORY):
    data = generate_random_data()
    rand_id = randint(1, MAX_ID_RANGE)

    operations = ["INSERT", "UPDATE", "DELETE"]
    # 80% of the time, we want to insert a new record, 10% to update a record, and 10% to delete a record
    random_operation = choice(operations + ["INSERT"] * 8)
    
    # insert new record into the table
    insert_query = f"""
    INSERT INTO test.inventory ({','.join(data.keys())})
    VALUES ({','.join(['%s'] * len(data))})
    """

    # Update a record in the table
    update_query = """
        UPDATE test.inventory
        SET name = %s, modified_date = %s
        WHERE id = %s
    """

    # Delete a record from the table
    delete_query = """
        DELETE FROM test.inventory
        WHERE id = %s
    """

    # Switch case for random_operation
    if random_operation == "INSERT":
        cursor.execute(insert_query, list(data.values()))
    elif random_operation == "UPDATE":
        cursor.execute(update_query, (data["name"], data["modified_date"], rand_id))
    elif random_operation == "DELETE":
        cursor.execute(delete_query, (rand_id,))

    connection.commit()

