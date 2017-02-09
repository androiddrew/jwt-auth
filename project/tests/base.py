# project/server/tests/base.py

# I really don't like how he did the setup and teardown
# http://docs.sqlalchemy.org/en/latest/orm/session_transaction.html#joining-a-session-into-an-external-transaction-such-as-for-test-suites
#from sqlalchemy.orm import sessionmaker
from flask_testing import TestCase

from project.server import app, db

# Session = sessionmaker()


class BaseTestCase(TestCase):
    """ Base Tests """

    def create_app(self):
        app.config.from_object('project.server.config.TestingConfig')
        return app

    def setUp(self):
        db.create_all()
        db.session.commit()

    def tearDown(self):
        db.session.remove()
        db.drop_all()


