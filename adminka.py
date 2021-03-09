from flask_admin.contrib.sqla import ModelView
from flask_admin import AdminIndexView
from login_secure import get_authorization
import models


class MyAdminIndexView(AdminIndexView):
    def is_accessible(self):
        current_user = get_authorization()
        return current_user['access']


class MyModelView(ModelView):
    column_exclude_list = ('psw', 'author', 'post', 'owner_price', 'product', 'file')


def admin_initialization(admin_panel):
    admin_panel.add_views(MyModelView(models.Users, models.db.session), ModelView(models.Goods, models.db.session),
                          MyModelView(models.Posts, models.db.session), MyModelView(models.Tenders, models.db.session),
                          MyModelView(models.Files, models.db.session))
