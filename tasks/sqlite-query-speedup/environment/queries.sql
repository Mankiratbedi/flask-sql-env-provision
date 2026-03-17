-- Q1: Top customers by revenue in last 30 days
SELECT c.name, SUM(o.total_price) as revenue
FROM orders o JOIN customers c ON o.customer_id = c.id
WHERE o.created_at >= date('2026-03-16', '-30 days')
GROUP BY c.id ORDER BY revenue DESC LIMIT 20;

-- Q2: Products with declining sales (comparing two 30-day periods)
SELECT p.name, p.category,
       SUM(CASE WHEN o.created_at >= date('2026-03-16','-30 days') THEN o.quantity ELSE 0 END) as recent,
       SUM(CASE WHEN o.created_at BETWEEN date('2026-03-16','-60 days') AND date('2026-03-16','-31 days') THEN o.quantity ELSE 0 END) as prior
FROM products p LEFT JOIN orders o ON p.id = o.product_id
GROUP BY p.id HAVING prior > recent ORDER BY (prior - recent) DESC LIMIT 10;

-- Q3: Orders per region per status
SELECT region, status, COUNT(*) as cnt, AVG(total_price) as avg_price
FROM orders GROUP BY region, status ORDER BY region, cnt DESC;

-- Q4: High-value customers (gold/platinum tier) in top regions
SELECT c.name, c.tier, c.country, COUNT(o.id) as order_count, SUM(o.total_price) as lifetime_value
FROM customers c JOIN orders o ON c.id = o.customer_id
WHERE c.tier IN ('gold', 'platinum')
GROUP BY c.id
HAVING order_count >= 10
ORDER BY lifetime_value DESC LIMIT 20;

-- Q5: Daily order counts per region for last 30 days
SELECT region, created_at, COUNT(*) as daily_orders, SUM(total_price) as daily_revenue
FROM orders
WHERE created_at >= date('2026-03-16', '-30 days')
GROUP BY region, created_at
ORDER BY region, created_at;
