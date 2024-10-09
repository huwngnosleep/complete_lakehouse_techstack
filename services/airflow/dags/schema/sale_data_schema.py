CATEGORIES = {
    "name": "categories",
    "schema": [
        {"name": "category_id", "type": "BIGINT", "primary_key": True},
        {"name": "category_name", "type": "STRING"}
    ],
    "primary_key": ["category_id"],
    "table_type": "dim",
}

BRANDS = {
    "name": "brands",
    "schema": [
        {"name": "brand_id", "type": "BIGINT", "primary_key": True},
        {"name": "brand_name", "type": "STRING"}
    ],
    "primary_key": ["brand_id"],
    "table_type": "dim",   
}

PRODUCTS = {
    "name": "products",
    "schema": [
        {"name": "product_id", "type": "BIGINT", "primary_key": True},
        {"name": "product_name", "type": "STRING"},
        {"name": "brand_id", "type": "BIGINT"},
        {"name": "category_id", "type": "BIGINT"},
        {"name": "model_year", "type": "BIGINT"},
        {"name": "list_price", "type": "DOUBLE"},
    ],
    "primary_key": ["product_id"],
    "table_type": "dim",
}

CUSTOMERS = {
    "name": "customers",
    "schema": [
        {"name": "customer_id", "type": "BIGINT", "primary_key": True},
        {"name": "first_name", "type": "STRING"},
        {"name": "last_name", "type": "STRING"},
        {"name": "phone", "type": "STRING"},
        {"name": "email", "type": "STRING"},
        {"name": "street", "type": "STRING"},
        {"name": "city", "type": "STRING"},
        {"name": "state", "type": "STRING"},
        {"name": "zip_code", "type": "STRING"}
    ],
    "primary_key": ["customer_id"],
    "table_type": "dim",
}

STORES = {
    "name": "stores",
    "schema": [
        {"name": "store_id", "type": "BIGINT", "primary_key": True},
        {"name": "store_name", "type": "STRING"},
        {"name": "phone", "type": "STRING"},
        {"name": "email", "type": "STRING"},
        {"name": "street", "type": "STRING"},
        {"name": "city", "type": "STRING"},
        {"name": "state", "type": "STRING"},
        {"name": "zip_code", "type": "STRING"}
    ],
    "primary_key": ["store_id"],
    "table_type": "dim",
}

STAFFS = {
    "name": "staffs",
    "schema": [
        {"name": "staff_id", "type": "BIGINT", "primary_key": True},
        {"name": "first_name", "type": "STRING"},
        {"name": "last_name", "type": "STRING"},
        {"name": "email", "type": "STRING"},
        {"name": "phone", "type": "STRING"},
        {"name": "active", "type": "BIGINT"},
        {"name": "store_id", "type": "BIGINT"},
        {"name": "manager_id", "type": "DOUBLE"}
    ],
    "primary_key": ["staff_id"],
    "table_type": "dim",
}

ORDERS = {
    "name": "orders",
    "schema": [
        {"name": "order_id", "type": "BIGINT", "primary_key": True},
        {"name": "customer_id", "type": "BIGINT"},
        # Order status: 1 = Pending; 2 = Processing; 3 = Rejected; 4 = Completed
        {"name": "order_status", "type": "BIGINT"},
        {"name": "order_date", "type": "DATE"},
        {"name": "required_date", "type": "DATE"},
        {"name": "shipped_date", "type": "DATE"},
        {"name": "store_id", "type": "BIGINT"},
        {"name": "staff_id", "type": "BIGINT"}
    ],
    "primary_key": ["order_id"],
    "table_type": "fact",
}

ORDER_ITEMS = {
    "name": "order_items",
    "schema": [
        {"name": "order_id", "type": "BIGINT", "primary_key": True},
        {"name": "item_id", "type": "BIGINT", "primary_key": True},
        {"name": "product_id", "type": "BIGINT"},
        {"name": "quantity", "type": "BIGINT"},
        {"name": "list_price", "type": "DOUBLE"},
        {"name": "discount", "type": "DOUBLE"}
    ],
    "primary_key": ["order_id", "item_id"],
    "table_type": "dim",
}

STOCKS = {
    "name": "stocks",
    "schema": [
        {"name": "store_id", "type": "BIGINT", "primary_key": True},
        {"name": "product_id", "type": "BIGINT", "primary_key": True},
        {"name": "quantity", "type": "BIGINT"}
    ],
    "primary_key": ["store_id", "product_id"],
    "table_type": "dim",
}

ALL_TABLES = {
    CATEGORIES["name"]: CATEGORIES,
    BRANDS["name"]: BRANDS,
    PRODUCTS["name"]: PRODUCTS,
    CUSTOMERS["name"]: CUSTOMERS,
    STORES["name"]: STORES,
    STAFFS["name"]: STAFFS,
    ORDERS["name"]: ORDERS,
    ORDER_ITEMS["name"]: ORDER_ITEMS,
    STOCKS["name"]: STOCKS,
}