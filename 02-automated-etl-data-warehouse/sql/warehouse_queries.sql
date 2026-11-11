SELECT year,month,orders,units,ROUND(revenue,2) revenue,ROUND(aov,2) aov FROM mart_monthly_sales ORDER BY year,month;
SELECT p.product_name,p.category,SUM(f.net_sales) revenue FROM fact_sales f JOIN dim_product p USING(product_id) GROUP BY 1,2 ORDER BY 3 DESC;
SELECT * FROM etl_run_log ORDER BY started_at DESC;
