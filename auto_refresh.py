# auto_refresh_csv.py
import time, random, psycopg2
from datetime import date
from dateutil.relativedelta import relativedelta  # pip install python-dateutil

DSN = "host=localhost port=5432 dbname=e-commerce user=postgres password=0000"

def next_month(d: date) -> date:
    # всегда 1-е число следующего месяца
    return (d.replace(day=1) + relativedelta(months=1))

def main():
    print("Auto-refresh CSV started 🚀 (writing to public.orders_monthly_csv)")
    with psycopg2.connect(DSN) as conn:
        conn.autocommit = True
        cur = conn.cursor()

        # возьмём последний месяц из CSV-таблицы
        cur.execute("SELECT COALESCE(MAX(month::date), DATE '2016-08-01') FROM public.orders_monthly_csv;")
        last_month = cur.fetchone()[0]
        if isinstance(last_month, str):
            last_month = date.fromisoformat(last_month)

        # приблизим стартовую интенсивность к последнему значению
        cur.execute("""
            SELECT orders_count
            FROM public.orders_monthly_csv
            WHERE month = (SELECT MAX(month) FROM public.orders_monthly_csv);
        """)
        row = cur.fetchone()
        base = row[0] if row and row[0] is not None else 300

        while True:
            m = next_month(last_month)
            # сгенерим реалистичную динамику вокруг base (можно подправить под свой датасет)
            delta = random.randint(-250, 350)
            value = max(0, base + delta)

            cur.execute(
                "INSERT INTO public.orders_monthly_csv (month, orders_count) VALUES (%s, %s) ON CONFLICT DO NOTHING;",
                (m, int(value))
            )
            print(f"CSV+ {m.isoformat()} -> {value}")

            last_month = m
            base = value
            time.sleep(8)   # интервал 5–20 сек по заданию; поставил 8 секунд

if __name__ == "__main__":
    main()
