from minio import Minio
from minio.error import S3Error
import pandas as pd
import io
import csv
from datetime import datetime, timedelta
import numpy as np
import os

# Initialize MinIO client
client = Minio(
    "localhost:9001",
    access_key="minioadmin",
    secret_key="minioadmin123",
    secure=False
)

def create_bucket_if_not_exists(bucket_name):
    """Create bucket if it doesn't exist"""
    try:
        if not client.bucket_exists(bucket_name):
            client.make_bucket(bucket_name)
            print(f"✓ Created bucket: {bucket_name}")
        else:
            print(f"✓ Bucket '{bucket_name}' already exists")
        return True
    except S3Error as e:
        print(f"✗ Error with bucket: {e}")
        return False

def upload_csv_from_dataframe(bucket_name, object_name, dataframe):
    """Upload a pandas DataFrame as CSV to MinIO"""
    try:
        # Convert DataFrame to CSV string
        csv_buffer = io.StringIO()
        dataframe.to_csv(csv_buffer, index=False)
        csv_string = csv_buffer.getvalue()
        
        # Convert string to bytes
        csv_bytes = csv_string.encode('utf-8')
        
        # Upload to MinIO
        result = client.put_object(
            bucket_name,
            object_name,
            io.BytesIO(csv_bytes),
            len(csv_bytes),
            content_type='text/csv'
        )
        
        print(f"✓ Successfully uploaded DataFrame as CSV: {object_name}")
        print(f"  ETag: {result.etag}")
        print(f"  Size: {len(csv_bytes)} bytes")
        return True
        
    except Exception as e:
        print(f"✗ Error uploading DataFrame: {e}")
        return False

def upload_csv_from_file(bucket_name, local_file_path, object_name=None):
    """Upload a local CSV file to MinIO"""
    try:
        # If no object name provided, use the filename
        if object_name is None:
            object_name = os.path.basename(local_file_path)
        
        # Check if file exists
        if not os.path.exists(local_file_path):
            print(f"✗ File not found: {local_file_path}")
            return False
        
        # Upload file directly
        result = client.fput_object(
            bucket_name,
            object_name,
            local_file_path,
            content_type='text/csv'
        )
        
        file_size = os.path.getsize(local_file_path)
        print(f"✓ Successfully uploaded local file: {local_file_path}")
        print(f"  Stored as: {object_name}")
        print(f"  ETag: {result.etag}")
        print(f"  Size: {file_size} bytes")
        return True
        
    except Exception as e:
        print(f"✗ Error uploading file: {e}")
        return False

def create_sample_csv_data():
    """Create sample CSV data for demonstration"""
    
    # Example 1: Sales data
    sales_data = pd.DataFrame({
        'transaction_id': range(1, 1001),
        'customer_id': np.random.randint(1000, 9999, 1000),
        'product_name': np.random.choice(['Laptop', 'Phone', 'Tablet', 'Headphones', 'Mouse'], 1000),
        'category': np.random.choice(['Electronics', 'Accessories', 'Computers'], 1000),
        'price': np.round(np.random.uniform(10.99, 999.99, 1000), 2),
        'quantity': np.random.randint(1, 10, 1000),
        'discount_pct': np.round(np.random.uniform(0, 0.3, 1000), 2),
        'sale_date': pd.date_range('2024-01-01', periods=1000, freq='H'),
        'sales_rep': np.random.choice(['Alice', 'Bob', 'Charlie', 'Diana', 'Eve'], 1000),
        'region': np.random.choice(['North', 'South', 'East', 'West'], 1000)
    })
    
    # Calculate total amount
    sales_data['total_amount'] = (sales_data['price'] * sales_data['quantity'] * 
                                 (1 - sales_data['discount_pct']))
    
    return sales_data

def create_time_series_data():
    """Create time series data for demonstration"""
    
    # Generate hourly data for a week
    dates = pd.date_range('2024-01-01', periods=168, freq='H')  # 7 days * 24 hours
    
    time_series_data = pd.DataFrame({
        'timestamp': dates,
        'temperature': 20 + 10 * np.sin(np.arange(168) * 2 * np.pi / 24) + np.random.normal(0, 2, 168),
        'humidity': 50 + 20 * np.sin(np.arange(168) * 2 * np.pi / 24 + np.pi/4) + np.random.normal(0, 5, 168),
        'pressure': 1013 + 10 * np.sin(np.arange(168) * 2 * np.pi / 48) + np.random.normal(0, 3, 168),
        'wind_speed': np.maximum(0, 5 + 3 * np.sin(np.arange(168) * 2 * np.pi / 12) + np.random.normal(0, 2, 168)),
        'sensor_id': np.random.choice(['TEMP_01', 'TEMP_02', 'TEMP_03'], 168),
        'location': np.random.choice(['Building_A', 'Building_B', 'Outdoor'], 168)
    })
    
    # Round numeric values
    time_series_data['temperature'] = time_series_data['temperature'].round(1)
    time_series_data['humidity'] = time_series_data['humidity'].round(1)
    time_series_data['pressure'] = time_series_data['pressure'].round(2)
    time_series_data['wind_speed'] = time_series_data['wind_speed'].round(1)
    
    return time_series_data

def create_local_csv_file(filename, dataframe):
    """Create a local CSV file from DataFrame for testing file upload"""
    try:
        dataframe.to_csv(filename, index=False)
        print(f"✓ Created local CSV file: {filename}")
        return True
    except Exception as e:
        print(f"✗ Error creating local file: {e}")
        return False

def upload_csv_with_custom_path(bucket_name, dataframe, year, month, day, filename):
    """Upload CSV with organized path structure (data lake pattern)"""
    
    # Create organized path: data/year=2024/month=01/day=15/filename.csv
    object_path = f"data/year={year}/month={month:02d}/day={day:02d}/{filename}"
    
    success = upload_csv_from_dataframe(bucket_name, object_path, dataframe)
    if success:
        print(f"  Organized path: {object_path}")
    return success

def upload_multiple_csv_files(bucket_name):
    """Upload multiple CSV files with different structures"""
    
    print("=" * 60)
    print("UPLOADING MULTIPLE CSV FILES")
    print("=" * 60)
    
    # 1. Sales data
    print("\n1. Uploading sales data...")
    sales_df = create_sample_csv_data()
    upload_csv_from_dataframe(bucket_name, "sales_data_2024.csv", sales_df)
    
    # 2. Time series data
    print("\n2. Uploading time series data...")
    ts_df = create_time_series_data()
    upload_csv_from_dataframe(bucket_name, "sensor_readings_week1.csv", ts_df)
    
    # 3. Organized data lake structure
    print("\n3. Uploading with data lake structure...")
    today = datetime.now()
    upload_csv_with_custom_path(
        bucket_name, 
        sales_df.head(100),  # Just first 100 rows
        today.year, 
        today.month, 
        today.day,
        "daily_sales.csv"
    )
    
    # 4. Create and upload from local file
    print("\n4. Creating and uploading local file...")
    local_filename = "temp_local_data.csv"
    if create_local_csv_file(local_filename, ts_df.head(50)):
        upload_csv_from_file(bucket_name, local_filename, "uploaded_from_local.csv")
        # Clean up
        try:
            os.remove(local_filename)
            print(f"✓ Cleaned up local file: {local_filename}")
        except:
            pass

def list_uploaded_files(bucket_name):
    """List all uploaded CSV files"""
    try:
        print(f"\n📁 Files in bucket '{bucket_name}':")
        print("-" * 50)
        
        objects = client.list_objects(bucket_name, recursive=True)
        csv_files = []
        
        for obj in objects:
            if obj.object_name.endswith('.csv'):
                csv_files.append(obj)
                print(f"📄 {obj.object_name}")
                print(f"   Size: {obj.size:,} bytes")
                print(f"   Modified: {obj.last_modified}")
                print()
        
        print(f"Total CSV files: {len(csv_files)}")
        return csv_files
        
    except Exception as e:
        print(f"✗ Error listing files: {e}")
        return []

def read_csv_back(bucket_name, object_name):
    """Read a CSV file back from MinIO to verify it was uploaded correctly"""
    try:
        print(f"\n📖 Reading back: {object_name}")
        print("-" * 40)
        
        # Get the object
        response = client.get_object(bucket_name, object_name)
        
        # Read into pandas DataFrame
        df = pd.read_csv(response)
        
        print(f"✓ Successfully read CSV file")
        print(f"  Shape: {df.shape}")
        print(f"  Columns: {list(df.columns)}")
        print("\nFirst 3 rows:")
        print(df.head(3))
        
        # Clean up connection
        response.close()
        response.release_conn()
        
        return df
        
    except Exception as e:
        print(f"✗ Error reading CSV: {e}")
        return None

def main():
    """Main function to demonstrate CSV upload operations"""
    
    bucket_name = "data-lake"
    
    print("🚀 MinIO CSV Upload Examples")
    print("=" * 60)
    
    # Create bucket
    if not create_bucket_if_not_exists(bucket_name):
        return
    
    # Upload multiple CSV files
    upload_multiple_csv_files(bucket_name)
    
    # List uploaded files
    csv_files = list_uploaded_files(bucket_name)
    
    # Read back one file to verify
    if csv_files:
        first_file = csv_files[0].object_name
        read_csv_back(bucket_name, first_file)
    
    print("\n✅ CSV upload demonstration complete!")
    print(f"\n🌐 View files in MinIO Console: http://localhost:9090")
    print("   Username: minioadmin")
    print("   Password: minioadmin123")

if __name__ == "__main__":
    main()
