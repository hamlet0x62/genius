import pytest
from genius import create_app
from genius import db as database
from genius.db import *


@pytest.fixture(scope='module')
def app():
    app = create_app()
    database.init_db(app)
    return app


@pytest.fixture(scope='module')
def cli(app):
    return app.test_client()


@pytest.fixture(scope='module', autouse=True)
def models(app):
    with app.app_context():
        database.db.drop_all()
        database.db.create_all()
        test_school = School.create_or_get(school_addr="Nanchang.Jiangxi",
                                           school_name="JEFU", school_tel="8380000")

        lend_limitation = LendLimitation.create_or_get(limit_days=30, limit_nums=10)
        default_r = Role.create_or_get(role_name="Normal", limit_type_id=lend_limitation.id)
        branch = Branch.create_or_get(branch_name="Disney Land",
                                      school=test_school,
                                      branch_addr=test_school.school_addr + "NB534",
                                      branch_tel=test_school.school_tel)
        c = Category.create_or_get(category_name="Fictions")
        b = Book.create_or_get(name="A Tale of 2 cities", author="Charles Dikens",
                               isbn="I372.2", categories=[c])
        ''.strip()

        simon = User.create_or_get(username="itsimon", email="i@aboutsimond.me", role=default_r)
        jerry = User.create_or_get(username="itsjerry", nickname="Jerry", email="i@jry.me", role=default_r)
