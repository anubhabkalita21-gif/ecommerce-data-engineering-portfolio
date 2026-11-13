-- 1. Monthly Revenue Trends
SELECT
    year,
    month,
    orders,
    units,
    ROUND(revenue, 2) AS revenue,
    ROUND(aov, 2) AS average_order_value
FROM mart_monthly_sales
ORDER BY year, month;


-- 2. Top 10 Products by Revenue
SELECT
    p.product_id,
    p.product_name,
    p.category,
    SUM(f.quantity) AS units_sold,
    ROUND(SUM(f.net_sales), 2) AS total_revenue
FROM fact_sales f
JOIN dim_product p
    ON f.product_id = p.product_id
WHERE LOWER(TRIM(f.order_status)) NOT IN ('cancelled', 'returned')
GROUP BY
    p.product_id,
    p.product_name,
    p.category
ORDER BY total_revenue DESC
LIMIT 10;


-- 3. Customer Purchase Analysis
SELECT
    c.customer_id,
    c.email,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(SUM(f.net_sales), 2) AS lifetime_revenue,
    ROUND(AVG(f.net_sales), 2) AS average_order_value
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_id = c.customer_id
WHERE LOWER(TRIM(f.order_status)) NOT IN ('cancelled', 'returned')
GROUP BY c.customer_id, c.email
ORDER BY lifetime_revenue DESC;


-- 4. City-wise Revenue Ranking
SELECT
    c.city,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(SUM(f.net_sales), 2) AS total_revenue
FROM fact_sales f
JOIN dim_customer c
    ON f.customer_id = c.customer_id
WHERE LOWER(TRIM(f.order_status)) NOT IN ('cancelled', 'returned')
GROUP BY c.city
ORDER BY total_revenue DESC;


-- 5. Product Category Performance
SELECT
    p.category,
    SUM(f.quantity) AS units_sold,
    COUNT(DISTINCT f.order_id) AS total_orders,
    ROUND(SUM(f.net_sales), 2) AS total_revenue
FROM fact_sales f
JOIN dim_product p
    ON f.product_id = p.product_id
WHERE LOWER(TRIM(f.order_status)) NOT IN ('cancelled', 'returned')
GROUP BY p.category
ORDER BY total_revenue DESC;


-- 6. ETL Execution History
SELECT *
FROM etl_run_log
ORDER BY started_at DESC;