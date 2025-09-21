-- 1 топ-5 штатов по сумме выручки 
select c.customer_state, sum(op.payment_value) as total_revenue
from orders o
join customers c on o.customer_id = c.customer_id
join order_payments op on o.order_id = op.order_id
group by c.customer_state
order by total_revenue desc
limit 5;

-- 2 среднее время доставки по категориям товаров 
select ct.product_category_name_english,
       round(avg(extract(epoch from (o.order_delivered_customer_date - o.order_purchase_timestamp)) / 86400), 2) as avg_days
from orders o
join order_items oi on o.order_id = oi.order_id
join products p on oi.product_id = p.product_id
join category_translation ct on p.product_category_name = ct.product_category_name
where o.order_delivered_customer_date is not null
group by ct.product_category_name_english
order by avg_days desc
limit 10;

-- 3 заказы без отзывов 
select o.order_id
from orders o
left join order_reviews r on o.order_id = r.order_id
where r.review_id is null
limit 20;

-- 4 все заказы и продавцы 
select oi.order_id, s.seller_id
from sellerxs s
right join order_items oi on s.seller_id = oi.seller_id
limit 20;

-- 5 количество заказов, где участвовало более одного продавца 
select o.order_id, count(distinct oi.seller_id) as seller_count
from orders o
join order_items oi on o.order_id = oi.order_id
group by o.order_id
having count(distinct oi.seller_id) > 1
limit 15;

-- 6 распределение типов оплат по заказам 
select payment_type, count(*) as num_payments
from order_payments
group by payment_type
order by num_payments desc;

-- 7 средняя оценка отзывов по штатам
select c.customer_state, round(avg(r.review_score),2) as avg_score
from order_reviews r
join orders o on r.order_id = o.order_id
join customers c on o.customer_id = c.customer_id
group by c.customer_state
order by avg_score desc
limit 10;

-- 8 топ-10 категорий по общей выручке 
select ct.product_category_name_english, sum(oi.price) as revenue
from order_items oi
join products p on oi.product_id = p.product_id
join category_translation ct on p.product_category_name = ct.product_category_name
group by ct.product_category_name_english
order by revenue desc
limit 10;

-- 9 количество заказов по статусу 
select order_status, count(*) as total_orders
from orders
group by order_status
order by total_orders desc;

-- 10 распределение оценок с процентами
select review_score,
       count(*) as total_reviews,
       round(100.0 * count(*) / sum(count(*)) over(), 2) as percentage
from order_reviews
group by review_score
order by review_score;
