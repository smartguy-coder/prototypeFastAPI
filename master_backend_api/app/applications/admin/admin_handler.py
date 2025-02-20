from fastapi import FastAPI
from sqladmin import Admin

from applications.admin.admin_auth import AdminAuth
from applications.admin.admin_models import CategoryAdmin, UserAdmin
from applications.base_model_and_mixins.base_models import sync_engine
from settings import settings


def add_sqladmin_interface(app: FastAPI):
    # https://aminalaee.dev/sqladmin/configurations/
    # http://127.0.0.1:10000/api/admin/user/list
    authentication_backend = AdminAuth(secret_key=settings.ADMIN_SECRET_KEY)
    admin = Admin(app, sync_engine, authentication_backend=authentication_backend)

    models = (UserAdmin, CategoryAdmin)
    for model in models:
        admin.add_view(model)
