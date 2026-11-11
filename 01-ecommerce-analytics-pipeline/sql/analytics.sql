SELECT month, orders, ROUND(revenue,2) revenue, ROUND(aov,2) average_order_value FROM monthly_kpis ORDER BY month;
SELECT category, ROUND(SUM(net_sales),2) revenue FROM category_revenue GROUP BY category ORDER BY revenue DESC;
SELECT city, ROUND(net_sales,2) revenue FROM city_revenue ORDER BY revenue DESC;
