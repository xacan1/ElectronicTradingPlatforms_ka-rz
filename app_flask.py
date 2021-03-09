import os
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_admin import Admin
from adminka import MyAdminIndexView
import config

# создание экземпляра приложения
app = Flask(__name__)
app.config.from_object(os.environ.get('FLASK_ENV') or 'config.ProductionConfig')

# инициализирует расширения
db = SQLAlchemy(app)
admin_panel = Admin(app, 'Admin panel', template_mode='bootstrap3', index_view=MyAdminIndexView())
