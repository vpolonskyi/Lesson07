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
def roles():
    return [
        # {"name": "Bubolog Hero", "type": "Junior topotun", "level": 3, "book": book_url},
        {"name": "Bubolog Hero", "type": "Junior topotun", "level": 3},
        {"name": "New Bubolog Hero", "type": "God of topotun", "level": 800},
        {"name": "Newest Bubolog Hero", "type": "Just God", "level": 99999999}]


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
    objs = obj_create(conn, urn_b, urn_r, objects=books)
    book_id = objs[0]["id"]
    fullroles = []
    for role in roles:
        role.update({"book": f"http://{conn.host}{urn_b}{book_id}"})
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


def test_book_create(conn, cleaner, books, urn_b):
    obj_created = []
    for book in books:
        print("\nCreating book", book)
        conn.request("POST",
                     urn_b,
                     json.dumps(book),
                     {"Content-Type": "application/json"}
                     )
        stat = conn.getresponse()
        assert stat.status == 201, "Http server return unexpected code while creating object"

        resp = json.loads(stat.read().decode('utf-8'))
        book.update({"id": resp["id"]})
        assert book == resp, "Created object does not match inputted data"

        cleaner.append(urn_b + str(resp["id"]))
        print("Book ID", resp["id"], "added to cleaner list")
        obj_created.append(book)

        conn.request("GET", urn_b)
        stat = conn.getresponse()
        resp = json.loads(stat.read().decode('utf-8'))
        assert book in resp, "Target page doesn't contain created object"

    for obj in obj_created:
        conn.request("GET", urn_b + str(obj["id"]))
        stat = conn.getresponse()
        assert stat.status == 200, "Http server return unexpected code while reading object by ID"
        resp = json.loads(stat.read().decode('utf-8'))
        assert obj == resp, "Readed object does not match created object"
