# Data-Visualization
Olist E-commerce Analytics
Olist is a large Brazilian e-commerce marketplace that connects small businesses to major online platforms. The company provides sellers with infrastructure for managing products, orders, logistics, and payments.
As a data analyst, my role is to analyze sales, payments, customer behavior, and logistics to uncover insights that support business decisions.

Project Overview

This project builds a PostgreSQL database from the Olist e-commerce dataset (orders, customers, sellers, payments, reviews, products)
The goal is to perform structured analytics, create an ERD schema, and write queries to answer key business questions.

The project includes:

Database ERD schema with relationships 

SQL queries 

Python script to run queries directly from PostgreSQL

Tools & Technologies

PostgreSQL 

Python 3.12

psycopg2 

pandas 

SQLAlchemy

pgAdmin 

GitHub

Project Structure
Olist-Analytics/
 ┣ main.py              # Python script for running SQL queries
 ┣ queries.sql          # 10 SQL queries with comments
 ┣ erd.png              # ERD diagram of the database
 ┣ README.md            # Documentation



Running Python Script

Install dependencies:

pip install psycopg2 pandas sqlalchemy


Run script:

python3 main.py



ERD Schema

The ERD shows all tables (orders, order_items, products, customers, sellers, geolocation, payments, reviews, category_translation) and their relationships via primary/foreign keys.



How to Run the Project

Clone repository:

git clone https://github.com/yourusername/Olist-Analytics.git
cd Olist-Analytics


Set up PostgreSQL database:

psql -U postgres -d ecommerce -f queries.sql


Run Python script:

python3 main.py
