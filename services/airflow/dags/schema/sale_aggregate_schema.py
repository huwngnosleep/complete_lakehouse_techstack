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
    ],
    "order_key": "date(order_date)"
}

HUMAN_RESOURCE = {
    "name": "human_resource",
    "create_table_command": """
        CREATE OR REPLACE TABLE iceberg.aggr_warehouse.human_resource
        USING parquet
        AS
        select
            staff.staff_id, 
            first_value(concat(staff.first_name, ' ', staff.last_name)) as staff_full_name,
            first_value(staff.email) as staff_email,
            first_value(staff.phone) as staff_phone,
            first_value(store.store_id) as store_id,
            first_value(store.store_name) as store_name,
            first_value(concat('US-',store.state)) as store_state,
            first_value(staff.manager_id) as manager_id,
            first_value(concat(manager.first_name, ' ', manager.last_name)) as manager_full_name,
            sum(oi.list_price * oi.quantity) as revenue,
            sum(oi.list_price * oi.quantity * oi.discount) as discount_revenue,
            sum(oi.list_price * oi.quantity - oi.list_price * oi.quantity * oi.discount) as net_revenue
        from iceberg.warehouse.staffs staff
        JOIN iceberg.warehouse.stores store on staff.store_id = store.store_id
        LEFT JOIN iceberg.warehouse.staffs manager on staff.manager_id = manager.staff_id
        JOIN iceberg.warehouse.orders o on o.staff_id = staff.staff_id
        JOIN iceberg.warehouse.order_items oi ON o.order_id = oi.order_id
        group by 1
    """,
    "schema": [
        {"name": "staff_id", "type": "BIGINT"}, 
        {"name": "staff_full_name", "type": "STRING"}, 
        {"name": "staff_email", "type": "String"}, 
        {"name": "staff_phone", "type": "String"}, 
        {"name": "store_id", "type": "BIGINT"}, 
        {"name": "store_name", "type": "String"},
        {"name": "store_state", "type": "String"},
        {"name": "manager_id", "type": "BIGINT"}, 
        {"name": "manager_full_name", "type": "STRING"},
        {"name": "revenue", "type": "DOUBLE"}, 
        {"name": "discount_revenue", "type": "DOUBLE"}, 
        {"name": "net_revenue", "type": "DOUBLE"}
    ],
    "order_key": "staff_id"
}

SALE_AGGREGATE_TABLES = {
    REVENUE_BY_TIME["name"]: REVENUE_BY_TIME,
    HUMAN_RESOURCE["name"]: HUMAN_RESOURCE,
} 