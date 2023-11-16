import mysql.connector
import random
import string

# MySQL connection parameters
host = "localhost"
user = "root"
password = "rootpassword"
database = "test"

# Number of records to insert
num_records = 1000000

# Function to generate random string
def generate_random_string(length):
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))

# Establish a connection to MySQL
conn = mysql.connector.connect(
    host=host,
    user=user,
    password=password,
    database=database
)

# Create a cursor object to execute SQL queries
cursor = conn.cursor()

# Define the table schema
# table_schema = (
#     "CREATE TABLE IF NOT EXISTS test ("
#     "id INT AUTO_INCREMENT PRIMARY KEY,"
#     "name VARCHAR(255),"
#     "value INT)"
# )

# # Execute the CREATE TABLE query
# cursor.execute(table_schema)

# Generate and insert random data
for _ in range(num_records):
    name = generate_random_string(10)
    id = random.randint(1, 1000000)
    
    insert_query = f"INSERT INTO test (id, name) VALUES ('{id}', '{name}')"
    cursor.execute(insert_query)

# Commit the changes and close the connection
conn.commit()
cursor.close()
conn.close()

print(f"{num_records} random records inserted into the table.")
