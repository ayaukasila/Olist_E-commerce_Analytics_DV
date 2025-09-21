import psycopg2
import pandas as pd

conn = psycopg2.connect(
    dbname="e-commerce",
    user="postgres",
    password="0000",
    host="localhost",
    port="5432"
)

queries = [
    "SELECT COUNT(*) FROM public.orders;",
    "SELECT payment_type, ROUND(AVG(payment_value),2) AS avg_payment FROM public.order_payments GROUP BY payment_type;",
    """SELECT ct.product_category_name_english AS category, 
              SUM(oi.price) AS total_sales
       FROM public.order_items oi
       JOIN public.products p ON oi.product_id = p.product_id
       JOIN public.category_translation ct ON p.product_category_name = ct.product_category_name
       GROUP BY category
       ORDER BY total_sales DESC
       LIMIT 10;"""
]


for q in queries:
    df = pd.read_sql(q, conn)
    print(df)

conn.close()
