import psycopg2
import pandas as pd
import matplotlib.pyplot as plt
import plotly.express as px
import numpy as np
from openpyxl import load_workbook
from openpyxl.formatting.rule import ColorScaleRule
import os

os.makedirs('charts', exist_ok=True)
os.makedirs('exports', exist_ok=True)

conn = psycopg2.connect(
    dbname="e-commerce",
    user="postgres",
    password="0000",
    host="localhost",
    port="5432"
)

def create_analytical_charts():
    print("Создание аналитических графиков...")
   # 1. pie chart с таблицей данных
    query_pie = """
with status_stats as (
    select 
        order_status,
        count(*) as total_orders,
        100.0 * count(*) / sum(count(*)) over() as percentage
    from orders 
    group by order_status
)
select 
    case 
        when percentage >= 1 then order_status
        else 'other'
    end as status_group,
    sum(total_orders) as total_orders,
    round(sum(percentage), 2) as total_percentage
from status_stats
group by 
    case 
        when percentage >= 1 then order_status
        else 'other'
    end
order by total_orders desc
"""
    df_pie = pd.read_sql(query_pie, conn)

    plt.figure(figsize=(10, 8))

# ЦВЕТА ДЛЯ КАЖДОГО СТАТУСА
    colors = {
    'delivered': '#2E8B57',      # 🟢 Зеленый - УСПЕШНЫЕ ДОСТАВКИ
    'shipped': '#1E90FF',        # 🔵 Синий - ОТПРАВЛЕННЫЕ
    'processing': '#FFA500',     # 🟠 Оранжевый - В ОБРАБОТКЕ
    'approved': '#32CD32',       # 🟢 Лаймовый - ПОДТВЕРЖДЕННЫЕ
    'created': '#87CEEB',        # 🔵 Голубой - СОЗДАННЫЕ
    'invoiced': '#9370DB',       # 🟣 Фиолетовый - ВЫСТАВЛЕН СЧЕТ
    'other': '#A9A9A9'           # ⚫ Серый - ПРОЧИЕ СТАТУСЫ (<1%)
}

# Создаем список цветов для секторов в правильном порядке
    pie_colors = [colors[status] for status in df_pie['status_group']]

# Создаем подписи с процентами
    labels = [f"{status}\n({pct}%)" for status, pct in zip(df_pie['status_group'], df_pie['total_percentage'])]

    plt.pie(df_pie['total_orders'], 
        labels=labels,
        autopct='%1.1f%%',
        startangle=90,
        colors=pie_colors,
        wedgeprops={'edgecolor': 'white', 'linewidth': 1})

    plt.title('Распределение заказов по статусам\n(статусы <1% сгруппированы в "other")', 
          fontsize=14, fontweight='bold', pad=20)

    plt.tight_layout()
    plt.savefig('charts/pie_order_status.png', dpi=300, bbox_inches='tight')
    plt.close()

    print("Pie chart создан: распределение статусов заказов (с группой 'other')")
    # 2. bar chart - топ категорий по выручке
    query_bar = """
    select ct.product_category_name_english as category, 
           sum(oi.price) as revenue,
           count(distinct oi.order_id) as order_count
    from order_items oi
    join products p on oi.product_id = p.product_id
    join category_translation ct on p.product_category_name = ct.product_category_name
    group by ct.product_category_name_english
    order by revenue desc
    limit 10
    """
    df_bar = pd.read_sql(query_bar, conn)
    plt.figure(figsize=(12, 6))
    bars = plt.bar(df_bar['category'], df_bar['revenue'], color='skyblue', edgecolor='black')
    plt.title('Топ-10 категорий товаров по выручке')
    plt.xlabel('Категория товара')
    plt.ylabel('Выручка (R$)')
    plt.xticks(rotation=45, ha='right')
    
    for bar in bars:
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 1000,
                f'R$ {height:,.0f}', ha='center', va='bottom', fontsize=9)
    
    plt.tight_layout()
    plt.savefig('charts/bar_top_categories.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Bar chart создан: топ-10 категорий по выручке")

    # 3. horizontal bar - средние оценки по штатам
    query_hbar = """
    select c.customer_state, 
           round(avg(r.review_score), 2) as avg_score,
           count(r.review_id) as review_count
    from order_reviews r
    join orders o on r.order_id = o.order_id
    join customers c on o.customer_id = c.customer_id
    group by c.customer_state
    having count(r.review_id) > 50
    order by avg_score desc
    limit 10
    """
    df_hbar = pd.read_sql(query_hbar, conn)
    plt.figure(figsize=(12, 8))
    bars = plt.barh(df_hbar['customer_state'], df_hbar['avg_score'], color='lightgreen', edgecolor='black')
    plt.title('Топ-10 штатов по средней оценке отзывов')
    plt.xlabel('Средняя оценка')
    plt.ylabel('Штат')
    
    for bar in bars:
        width = bar.get_width()
        plt.text(width + 0.01, bar.get_y() + bar.get_height()/2., 
                f'{width:.2f}', ha='left', va='center')
    
    plt.tight_layout()
    plt.savefig('charts/hbar_avg_review_score.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Horizontal bar chart создан: средние оценки по штатам")

    # 4. line chart - динамика времени доставки
    query_line = """
    select date_trunc('month', o.order_purchase_timestamp) as month,
           round(avg(extract(epoch from (o.order_delivered_customer_date - o.order_purchase_timestamp)) / 86400), 2) as avg_delivery_days
    from orders o
    where o.order_delivered_customer_date is not null
      and o.order_purchase_timestamp >= '2017-01-01'
    group by month
    order by month
    """
    df_line = pd.read_sql(query_line, conn)
    df_line['month'] = pd.to_datetime(df_line['month'])
    
    plt.figure(figsize=(12, 6))
    plt.plot(df_line['month'], df_line['avg_delivery_days'], marker='o', linewidth=2, markersize=6, color='coral')
    plt.title('Динамика среднего времени доставки заказов')
    plt.xlabel('Месяц')
    plt.ylabel('Среднее время доставки (дни)')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    plt.tight_layout()
    plt.savefig('charts/line_delivery_trend.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Line chart создан: динамика времени доставки")

    # 5. histogram - распределение оценок
    query_hist = """
    select review_score,
           count(*) as total_reviews,
           round(100.0 * count(*) / sum(count(*)) over(), 2) as percentage
    from order_reviews
    group by review_score
    order by review_score
    """
    df_hist = pd.read_sql(query_hist, conn)
    plt.figure(figsize=(10, 6))
    bars = plt.bar(df_hist['review_score'], df_hist['total_reviews'], 
                   color='gold', edgecolor='black', alpha=0.8)
    plt.title('Распределение оценок в отзывах')
    plt.xlabel('Оценка')
    plt.ylabel('Количество отзывов')
    plt.grid(True, alpha=0.3, axis='y')
    
    for bar, percentage, total in zip(bars, df_hist['percentage'], df_hist['total_reviews']):
        height = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2., height + 100,
                f'{total:,}\n({percentage}%)', ha='center', va='bottom', fontsize=9)
    
    plt.savefig('charts/histogram_review_distribution.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Histogram создан: распределение оценок с процентами")

    # 6. scatter plot - связь цены и веса
    query_scatter = """
    select oi.price, 
           p.product_weight_g,
           ct.product_category_name_english as category,
           c.customer_state
    from order_items oi
    join products p on oi.product_id = p.product_id
    join category_translation ct on p.product_category_name = ct.product_category_name
    join orders o on oi.order_id = o.order_id
    join customers c on o.customer_id = c.customer_id
    where p.product_weight_g is not null 
      and p.product_weight_g > 0 
      and oi.price > 0
      and oi.price < 1000
      and p.product_weight_g < 5000
    limit 2000
    """
    df_scatter = pd.read_sql(query_scatter, conn)
    
    plt.figure(figsize=(12, 8))

    top_categories = df_scatter['category'].value_counts().head(5).index
    colors = ['red', 'blue', 'green', 'orange', 'purple']
    
    for i, category in enumerate(top_categories):
        category_data = df_scatter[df_scatter['category'] == category]
        plt.scatter(category_data['product_weight_g'], category_data['price'], 
                   color=colors[i], alpha=0.6, label=category, s=30)

    if len(df_scatter) > 1:
        z = np.polyfit(df_scatter['product_weight_g'], df_scatter['price'], 1)
        p = np.poly1d(z)
        plt.plot(df_scatter['product_weight_g'], p(df_scatter['product_weight_g']), 
                "r--", alpha=0.8, linewidth=2, label='Линия тренда')

    plt.title('Связь веса товара и цены по категориям')
    plt.xlabel('Вес товара (граммы)')
    plt.ylabel('Цена (R$)')
    plt.legend()
    plt.grid(True, alpha=0.3)
    plt.savefig('charts/scatter_weight_vs_price_analytical.png', dpi=300, bbox_inches='tight')
    plt.close()
    print("Scatter plot создан: связь веса и цены товаров")

def create_time_slider():
    print("Создание интерактивного графика с ползунком...")
    
    query = """
    select date_trunc('month', o.order_purchase_timestamp) as month,
           c.customer_state,
           count(distinct o.order_id) as order_count,
           avg(oi.price) as avg_price,
           sum(oi.price) as total_sales
    from orders o
    join customers c on o.customer_id = c.customer_id
    join order_items oi on o.order_id = oi.order_id
    where o.order_purchase_timestamp is not null
      and c.customer_state in (select customer_state from customers group by customer_state order by count(*) desc limit 8)
    group by month, c.customer_state
    having count(distinct o.order_id) > 5
    """
    df = pd.read_sql(query, conn)
    df['month'] = pd.to_datetime(df['month'])
    df['year_month'] = df['month'].dt.strftime('%Y-%m')
    
    fig = px.scatter(df, 
                    x="avg_price", 
                    y="order_count",
                    size="total_sales",
                    color="customer_state",
                    animation_frame="year_month",
                    title="Динамика заказов по штатам во времени",
                    labels={
                        "avg_price": "Средняя цена заказа (R$)", 
                        "order_count": "Количество заказов",
                        "customer_state": "Штат",
                        "total_sales": "Общая выручка",
                        "year_month": "Месяц"
                    },
                    hover_data=['total_sales'])
    
    fig.update_layout(
        width=1000,
        height=600
    )
    
    fig.write_html("charts/interactive_time_slider.html")
    print("Интерактивный график создан: charts/interactive_time_slider.html")
    
    fig.show()

def export_to_excel(dataframes_dict, filename):
    filepath = f'exports/{filename}'
    
    with pd.ExcelWriter(filepath, engine='openpyxl') as writer:
        for sheet_name, df in dataframes_dict.items():
            df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            workbook = writer.book
            worksheet = writer.sheets[sheet_name]
            
            worksheet.freeze_panes = "A2"
            
            worksheet.auto_filter.ref = worksheet.dimensions
            
            numeric_columns = df.select_dtypes(include=['number']).columns
            for col_idx, col_name in enumerate(numeric_columns, 1):
                col_letter = chr(64 + col_idx)
                range_str = f"{col_letter}2:{col_letter}{len(df)+1}"
                
                rule = ColorScaleRule(start_type="min", start_color="FFAA0000",
                                    end_type="max", end_color="FF00AA00")
                worksheet.conditional_formatting.add(range_str, rule)
    
    total_rows = sum(len(df) for df in dataframes_dict.values())
    total_sheets = len(dataframes_dict)
    
    print(f"Создан файл {filename}, {total_sheets} листов, {total_rows} строк")

def export_analytical_data():
    print("Экспорт данных в Excel...")
    
    queries_export = {
        'status_orders': """
            select order_status, 
                   count(*) as order_count,
                   round(100.0 * count(*) / sum(count(*)) over(), 2) as percentage
            from orders 
            group by order_status 
            order by order_count desc
        """,
        'top_categories': """
            select ct.product_category_name_english as category, 
                   sum(oi.price) as revenue,
                   count(distinct oi.order_id) as order_count,
                   round(avg(oi.price), 2) as avg_price
            from order_items oi
            join products p on oi.product_id = p.product_id
            join category_translation ct on p.product_category_name = ct.product_category_name
            group by ct.product_category_name_english
            order by revenue desc
            limit 15
        """,
        'states_reviews': """
            select c.customer_state as state, 
                   round(avg(r.review_score), 2) as avg_score,
                   count(r.review_id) as review_count,
                   min(r.review_score) as min_score,
                   max(r.review_score) as max_score
            from order_reviews r
            join orders o on r.order_id = o.order_id
            join customers c on o.customer_id = c.customer_id
            group by c.customer_state
            having count(r.review_id) > 10
            order by avg_score desc
        """,
        'payment_types': """
            select payment_type,
                   count(*) as payment_count,
                   round(avg(payment_value), 2) as avg_payment,
                   sum(payment_value) as total_payment,
                   round(100.0 * count(*) / sum(count(*)) over(), 2) as percentage
            from order_payments
            group by payment_type
            order by payment_count desc
        """
    }
    
    dataframes = {}
    for sheet_name, query in queries_export.items():
        print(f"Загрузка данных для листа: {sheet_name}")
        dataframes[sheet_name] = pd.read_sql(query, conn)
    
    export_to_excel(dataframes, 'ecommerce_analytical_report.xlsx')

def main():
    try:
        create_analytical_charts()
        
        create_time_slider()
        
        export_analytical_data()
        
        print("Все задачи выполнены успешно")
        print("Созданные файлы:")
        print("Графики: charts/")
        print("Excel: exports/")
        print("Интерактивный график: charts/interactive_time_slider.html")
        
    except Exception as e:
        print(f"Ошибка: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()