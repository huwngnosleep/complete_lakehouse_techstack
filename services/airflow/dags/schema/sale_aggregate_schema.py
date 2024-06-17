REVENUE_BY_TIME = {
    "name": "revenue_by_time",
    "create_table_command": """
        CREATE OR REPLACE TABLE iceberg.aggr_warehouse.revenue_by_time
        USING parquet
        AS
        SELECT
        o.order_id, o.customer_id, o.store_id, o.staff_id, 
        o.order_status, o.order_date,
        (oi.list_price * oi.quantity) as revenue,
        (oi.list_price * oi.quantity * oi.discount) as discount_revenue,
        (revenue - discount_revenue) as net_revenue
        FROM iceberg.warehouse.orders o
        JOIN iceberg.warehouse.order_items oi ON o.order_id = oi.order_id
    """
}

SALE_AGGREGATE_TABLES = {
    REVENUE_BY_TIME["name"]: REVENUE_BY_TIME,
}