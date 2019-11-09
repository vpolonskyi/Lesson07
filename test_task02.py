import http.client
import json
import pytest


@pytest.fixture(scope="session")
def urn_b():
    return "/books/"


@pytest.fixture(scope="session")
def urn_r():
    return "/roles/"


@pytest.fixture(scope="session")
def conn():
    host = "pulse-rest-testing.herokuapp.com"
    conn = http.client.HTTPConnection(host, timeout=10)
    print(conn, "established")
    yield conn
    print("Closing", conn)
    conn.close()
    print(conn, "closed")

@pytest.fixture
def cleaner(conn):
    clean = []
    yield clean
    print("Going to clean", clean)
    for urn in clean:
        conn.request("DELETE", urn)
        print("Object", urn, "cleaned")
        stat = conn.getresponse()
        stat.read()


@pytest.fixture
def books():
    return [
        {"title": "Bubology", "author": "Great Me"},
        {"title": "771234", "author": "77I"},
        {"title": "77#$$%^&*(*()", "author": "77I"},
        {"title": "77рпмроиоли", "author": "77I"}]


@pytest.fixture
def books_400():
    return [
        {"title": "Bubology"},
        {"author": "Great Me"},
        {"title": "Bubology", "author": "", "tome": "II"},
        {"title": "Bubology", "author": ""},
        {"title": "", "author": "Great Me"},
        "abc",
        123,
        [1, 2, 3],
        [{"title": "", "author": "Great Me"}, 123],
        {"title": "123456789012345678901234567890123456789012345678901", "author": "Great Me"},
        {"title": "Bubology", "author": "123456789012345678901234567890123456789012345678901"}]


@pytest.fixture
def roles():
    return [
        # {"name": "Bubolog Hero", "type": "Junior topotun", "level": 3, "book": book_url},
        {"name": "Bubolog Hero", "type": "Junior topotun", "level": 3},
        {"name": "New Bubolog Hero", "type": "God of topotun", "level": 800},
        {"name": "Newest Bubolog Hero", "type": "Just God", "level": 99999999},
        {"name": "Good old Bubolog Hero", "type": "Kid of topotun"}]

@pytest.fixture
def roles_400():
    return [
        {"name": "Bubolog Hero"},
        {"type": "Just God", "level": 99999999},
        {"name": "Bubolog Hero", "level": 3},
        # {"name": "New Bubolog Hero", "type": "God of topotun", "level": 800, "coolnest": "WOW!"},
        # {"name": "123456789012345678901234567890123456789012345678901", "type": "Junior topotun", "level": 3},
        # {"name": "Bubolog Hero", "type": "123456789012345678901234567890123456789012345678901", "level": 3},
        {"name": "Bubolog Hero", "type": "Junior topotun", "level": 123456789012345678901234567890123456789012345678901},
        "abc",
        123,
        [1, 2, 3],
        [{"title": "", "author": "Great Me"}, 123]]


def obj_create(conn, urn_b: str, urn_r: str, objects: list = None) -> list:
    """
    Create (if ID is None) or update (if ID is not None) book (if "title" not None) role (if "title" is None)
    :param conn: http.client connect object
    :param urn_b: urn of books
    :param urn_r: urn of roles
    :param objects: list of dicts containing books/roles
    :return: list of dicts created objects, like [{'title': 'Book1', 'author': '1st', 'id': 1},
     {'name': 'Hero', 'type': 'God', 'level': 5, 'book': 'http://host.com/books/3', 'id': 9}]
    """
    obj_created = []

    for obj in objects:
        if obj is None:
            break

        if obj.get("id") is None:
            method = "POST"
        else:
            method = "PUT"

        if obj.get("title"):
            urn = urn_b
            print("\nCreating book", obj)
        else:
            urn = urn_r
            print("\nCreating role", obj)

        conn.request(method,
                     urn,
                     json.dumps(obj),
                     {"Content-Type": "application/json"}
                     )
        stat = conn.getresponse()
        print(stat.status, stat.reason)
        resp = json.loads(stat.read().decode('utf-8'))
        obj.update({"id": resp["id"]})
        obj_created.append(obj)
    print("Objects", obj_created, "created")
    return obj_created


def test_obj_read(conn, urn_b, urn_r, cleaner, books, roles):
    print("\ntest_obj_read")
    objs = obj_create(conn, urn_b, urn_r, objects=books)
    valid_book_id = objs[0]["id"]
    fullroles = []
    for role in roles:
        if role.get("level") is None:
            role.update({"level": 0})
        role.update({"book": f"http://{conn.host}{urn_b}{valid_book_id}"})
        fullroles.append(role)
    objs.extend(obj_create(conn, urn_b, urn_r, objects=fullroles))

    conn.request("GET", urn_b)
    stat = conn.getresponse()
    resp_books = json.loads(stat.read().decode('utf-8'))

    conn.request("GET", urn_r)
    stat = conn.getresponse()
    resp_roles = json.loads(stat.read().decode('utf-8'))

    for obj in objs:
        if obj.get("title"):
            assert obj in resp_books, "Target page doesn't contain created object"
            urn = urn_b
        else:
            assert obj in resp_roles, "Target page doesn't contain created object"
            urn = urn_r
        cleaner.append(urn + str(obj["id"]))
        print("Object ID", obj["id"], "added to cleaner list")


def test_object_create(conn, cleaner, books, books_400, roles, roles_400, urn_b, urn_r):
    print("\ntest_object_create")
    obj_created = []
    objects = books + books_400 + roles + roles_400
    for obj in objects:
        print("\nCreating object", obj)
        if obj in books + books_400:
            urn = urn_b
        else:
            urn = urn_r
            obj.update({"book": f"http://{conn.host}{urn_b}{valid_book_id}"})
        conn.request("POST",
                     urn,
                     json.dumps(obj),
                     {"Content-Type": "application/json"}
                     )
        stat = conn.getresponse()

        if obj in books_400 + roles_400:
            resp = stat.read()
            assert stat.status == 400, "Http server return unexpected code while creating object"
            conn.request("GET", urn)
            stat = conn.getresponse()
            resp = json.loads(stat.read().decode('utf-8'))
            assert obj not in resp, "Target page unexpected contain created object"

        else:
            resp = json.loads(stat.read().decode('utf-8'))
            assert stat.status == 201, "Http server return unexpected code while creating object"
            if obj in books and stat.status == 201:
                valid_book_id = resp["id"]
            if obj in roles and obj.get("level") is None:
                obj.update({"level": 0})
            obj.update({"id": resp["id"]})
            assert obj == resp, "Created object does not match inputted data"

        if stat.status == 201:
            cleaner.append(urn + str(resp["id"]))
            print("Object ID", resp["id"], "added to cleaner list")
            obj_created.append(obj)

            conn.request("GET", urn)
            stat = conn.getresponse()
            resp = json.loads(stat.read().decode('utf-8'))
            assert obj in resp, "Target page doesn't contain created object"

    for obj in obj_created:
        if obj in books:
            urn = urn_b
        else:
            urn = urn_r
        conn.request("GET", urn + str(obj["id"]))
        stat = conn.getresponse()
        resp = json.loads(stat.read().decode('utf-8'))
        assert stat.status == 200, "Http server return unexpected code while reading object by ID"
        assert obj == resp, "Readed object does not match created object"

# def test_obj_update()