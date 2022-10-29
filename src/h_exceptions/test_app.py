import pytest
from fastapi.testclient import TestClient

from app import app, food_log, pwd_context

LAME_PASSWORD = "1234"  # noqa S105


# also from https://fastapi.tiangolo.com/tutorial/security/oauth2-jwt/
def _verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)


@pytest.fixture
def client():
    client = TestClient(app)
    return client


@pytest.fixture
def user():
    user = dict(id=1, username="user", password=LAME_PASSWORD)
    return user


@pytest.fixture
def food():
    food = dict(
        id=1,
        name="egg",
        serving_size="piece",
        kcal_per_serving=78,
        protein_grams=6.2,
        fibre_grams=0,
    )
    return food


@pytest.fixture
def food_entry1(user, food):
    payload = dict(id=1, user=user, food=food, number_servings=1.5)
    yield payload
    del food_log[1]


@pytest.fixture
def food_entry2(user, food):
    payload = dict(id=2, user=user, food=food, number_servings=26.5)
    yield payload
    try:
        del food_log[2]
    except KeyError:
        pass


@pytest.fixture(autouse=True)
def create_food_entries(client, food_entry1):
    client.post("/", json=food_entry1)


def test_cannot_insert_same_food_entry_id_twice(client, food_entry1):
    resp = client.post("/", json=food_entry1)
    assert resp.status_code == 400
    error = "Food entry already logged, use an update request"
    expected = {"detail": error}
    assert resp.json() == expected


def test_cannot_overeat(client, food_entry1, food_entry2):
    # food entry 1 is posted in the autouse fixture = 1.5 eggs
    # posting food entry 2 would lead of a consumption of:
    # 28 (1.5 + 26.5) x 78 kcal == 2.184 which is still < 2.250 = ok
    resp = client.post("/", json=food_entry2)
    assert resp.status_code == 201
    # however posting one more egg on top of that we go over max
    # daily kcal allowance = 29 x 78 kcal = 2.262 > 2.250 -> not ok
    food_entry3 = food_entry1.copy()
    food_entry3["id"] = 3
    food_entry3["number_servings"] = 1
    resp = client.post("/", json=food_entry3)
    assert resp.status_code == 400
    error = ("Cannot add more food than daily caloric "
             "allowance = 2250 kcal / day")
    expected = {"detail": error}
    assert resp.json() == expected