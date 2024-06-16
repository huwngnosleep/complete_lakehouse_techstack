CATEGORIES = {
    "name": "categories",
    "schema": [
        {"name": "category_id", "type": "BIGINT"},
        {"name": "category_name", "type": "STRING"}
    ],
    "table_type": "dim",
}

BRANDS = {
    "name": "brands",
    "schema": [
        {"name": "brand_id", "type": "BIGINT"},
        {"name": "brand_name", "type": "STRING"}
    ],
    "table_type": "dim",   
}

PRODUCTS = {
    "name": "products",
    "schema": [
        {"name": "product_id", "type": "BIGINT"},
        {"name": "product_name", "type": "STRING"},
        {"name": "brand_id", "type": "BIGINT"},
        {"name": "category_id", "type": "BIGINT"},
        {"name": "model_year", "type": "BIGINT"},
        {"name": "list_price", "type": "DOUBLE"},
    ],
    "table_type": "dim",
}

CUSTOMERS = {
    "name": "customers",
    "schema": [
        {"name": "customer_id", "type": "BIGINT"},
        {"name": "first_name", "type": "STRING"},
        {"name": "last_name", "type": "STRING"},
        {"name": "phone", "type": "STRING"},
        {"name": "email", "type": "STRING"},
        {"name": "street", "type": "STRING"},
        {"name": "city", "type": "STRING"},
        {"name": "state", "type": "STRING"},
        {"name": "zip_code", "type": "STRING"}
    ],
    "table_type": "dim",
}

STORES = {
    "name": "stores",
    "schema": [
        {"name": "store_id", "type": "BIGINT"},
        {"name": "store_name", "type": "STRING"},
        {"name": "phone", "type": "STRING"},
        {"name": "email", "type": "STRING"},
        {"name": "street", "type": "STRING"},
        {"name": "city", "type": "STRING"},
        {"name": "state", "type": "STRING"},
        {"name": "zip_code", "type": "STRING"}
    ],
    "table_type": "dim",
}

STAFFS = {
    "name": "staffs",
    "schema": [
        {"name": "staff_id", "type": "BIGINT"},
        {"name": "first_name", "type": "STRING"},
        {"name": "last_name", "type": "STRING"},
        {"name": "email", "type": "STRING"},
        {"name": "phone", "type": "STRING"},
        {"name": "active", "type": "BIGINT"},
        {"name": "store_id", "type": "BIGINT"},
        {"name": "manager_id", "type": "DOUBLE"}
    ],
    "table_type": "dim",
}

ORDERS = {
    "name": "orders",
    "schema": [
        {"name": "order_id", "type": "BIGINT"},
        {"name": "customer_id", "type": "BIGINT"},
        {"name": "order_status", "type": "BIGINT"},
        {"name": "order_date", "type": "DATE"},
        {"name": "required_date", "type": "DATE"},
        {"name": "shipped_date", "type": "DATE"},
        {"name": "store_id", "type": "BIGINT"},
        {"name": "staff_id", "type": "BIGINT"}
    ],
    "table_type": "fact",
}

ORDER_ITEMS = {
    "name": "order_items",
    "schema": [
        {"name": "order_id", "type": "BIGINT"},
        {"name": "item_id", "type": "BIGINT"},
        {"name": "product_id", "type": "BIGINT"},
        {"name": "quantity", "type": "BIGINT"},
        {"name": "list_price", "type": "DOUBLE"},
        {"name": "discount", "type": "DOUBLE"}
    ],
    "table_type": "dim",
}

STOCKS = {
    "name": "stocks",
    "schema": [
        {"name": "store_id", "type": "BIGINT"},
        {"name": "product_id", "type": "BIGINT"},
        {"name": "quantity", "type": "BIGINT"}
    ],
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