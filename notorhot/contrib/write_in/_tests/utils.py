from django.test import TestCase
import logging

logger = logging.getLogger(__name__)

# from http://stackoverflow.com/questions/502916/django-how-to-create-a-model-dynamically-just-for-testing
class ModelTestCase(TestCase):
    initiated = False
    apps = ()

    @classmethod
    def setUpClass(cls, *args, **kwargs):
        if not cls.initiated:
            for app_name in cls.apps:
                cls.create_models_from_app(app_name)
                cls.initiated = True

        super(TestCase, cls).setUpClass(*args, **kwargs)

    @classmethod
    def create_models_from_app(cls, app_name):
        """
        Manually create Models (used only for testing) from the specified string app name.
        Models are loaded from the module "<app_name>.models"
        """
        from django.db import connection, DatabaseError
        from django.db.models.loading import load_app

        app = load_app(app_name)
        from django.core.management import sql
        from django.core.management.color import no_style
        sql = sql.sql_create(app, no_style(), connection)
        cursor = connection.cursor()
        for statement in sql:
            try:
                cursor.execute(statement)
            except DatabaseError, excn:
                logger.debug(excn.message)