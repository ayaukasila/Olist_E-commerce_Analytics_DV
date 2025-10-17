# superset_config.py
import os

# Вставь сгенерированный ключ вместо 'your-secret-key-here'
SECRET_KEY = 'jOI9vn2FultxnamFRxyBq4RDnQIK1e5ycNiafIjEEbaDXYIPF4d35yi/'

# Дополнительные настройки
FEATURE_FLAGS = {
    "ENABLE_TEMPLATE_PROCESSING": True,
}

# Настройки БД
SQLALCHEMY_DATABASE_URI = 'sqlite:////app/superset.db'