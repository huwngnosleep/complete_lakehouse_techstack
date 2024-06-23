REVENUE_BY_TIME = {
    "name": "revenue_by_time",
    "create_table_command": """
        CREATE OR REPLACE TABLE iceberg.aggr_warehouse.revenue_by_time
        USING parquet
        AS
        SELECT
        o.order_id, o.customer_id, o.store_id, o.staff_id, 
         CASE
            WHEN o.order_status = 1 THEN 'Pending'
            WHEN o.order_status = 2 THEN 'Processing'
            WHEN o.order_status = 3 THEN 'Rejected'
            WHEN o.order_status = 4 THEN 'Completed'
        END as order_status, 
        o.order_date,
        (oi.list_price * oi.quantity) as revenue,
        (oi.list_price * oi.quantity * oi.discount) as discount_revenue,
        (revenue - discount_revenue) as net_revenue,
        CONCAT(c.first_name, ' ', c.last_name) as customer_fullname
        FROM iceberg.warehouse.orders o
        JOIN iceberg.warehouse.order_items oi ON o.order_id = oi.order_id
        LEFT JOIN iceberg.warehouse.customers c ON o.customer_id = c.customer_id
    """,
    "schema": [
        {"name": "order_id", "type": "BIGINT"}, 
        {"name": "customer_id", "type": "BIGINT"}, 
        {"name": "store_id", "type": "BIGINT"}, 
        {"name": "staff_id", "type": "BIGINT"}, 
        {"name": "order_status", "type": "BIGINT"}, 
        {"name": "order_date", "type": "DATE"}, 
        {"name": "revenue", "type": "DOUBLE"}, 
        {"name": "discount_revenue", "type": "DOUBLE"}, 
        {"name": "net_revenue", "type": "DOUBLE"}
    ]
}

SALE_AGGREGATE_TABLES = {
    REVENUE_BY_TIME["name"]: REVENUE_BY_TIME,
}