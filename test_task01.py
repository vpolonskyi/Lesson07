import requests
import unittest


class BookCRUD(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._burl = 'http://pulse-rest-testing.herokuapp.com/books/'
        cls._bpush = {"title": "Bubology", "author": "Great Me"}

    @classmethod
    def tearDownClass(cls) -> None:
        # requests.delete(cls._burl + "2508")
        # requests.delete(cls._burl + "2513")
        # requests.delete(cls._burl + "2515")
        # requests.delete(cls._burl + "2517")
        # requests.delete(cls._burl + "2519")
        res = requests.get(cls._burl)
        for i in res.json():
            if i["title"] == cls._bpush["title"] and i["author"] == cls._bpush["author"]:
                requests.delete(cls._burl + str(i["id"]))

    def setUp(self) -> None:
        self._res = requests.post(self._burl, self._bpush)
        self._bid = str(self._res.json()['id'])
        self._burlid = self._burl + self._bid

    def tearDown(self) -> None:
        requests.delete(self._burlid)

    def testCreateBook(self):
        self.assertEqual(201, self._res.status_code)
        get = requests.get(self._burlid).json()
        self.assertTrue(str(get["id"]) == str(self._bid) and
                        get["title"] == self._bpush["title"] and
                        get["author"] == self._bpush["author"])

    def testReadBookNotBySID(self):
        self.assertTrue(f'"title":"{self._bpush["title"]}","author":"{self._bpush["author"]}"' in
                        requests.get(self._burl).text)

    def testUpdateBook(self):
        push = {"title": "Bubology 2", "author": "Not so Great Me"}

        self.assertEqual(200, requests.put(self._burlid, push).status_code)
        get = requests.get(self._burlid)
        self.assertTrue(get.json()["title"] == push["title"] and get.json()["author"] == push["author"])

        self.assertEqual(200, requests.put(self._burlid, {"title": "Bubology 3"}).status_code)
        self.assertEqual(200, requests.put(self._burlid, {"author": "Super Great Me"}).status_code)
        get = requests.get(self._burlid)
        self.assertTrue(get.json()["title"] == "Bubology 3" and get.json()["author"] == "Super Great Me")

    def testDeleteBook(self):
        requests.delete(self._burlid)
        self.assertEqual(404, requests.get(self._burlid).status_code)
        self.assertFalse(f'"id":{self._bid},"' in requests.get(self._burl).text)

    def testWrongBookInput(self):
        self.assertEqual(400, requests.post(self._burl, {"title": "Bubology"}).status_code)
        self.assertEqual(415, requests.post(self._burl, "abc").status_code)
        with self.assertRaises(TypeError):
            requests.post(self._burl, 100)
        self.assertEqual(415, requests.put(self._burlid, "abc").status_code)
        with self.assertRaises(TypeError):
            requests.put(self._burlid, 100)

    def testLineOverflow(self):
        short = "12345678901234567890123456789012345678901234567890"
        long = "123456789012345678901234567890123456789012345678901"

        for i in [{"title": short, "author": "Great Me"},
                  {"title": "Bubology", "author": short},
                  {"title": short},
                  {"author": short}]:
            self.assertEqual(200, requests.put(self._burlid, i).status_code)
            if i.get("title") is not None and i.get("author") is not None:
                req = requests.post(self._burl, i)
                self.assertEqual(201, req.status_code)
                requests.delete(self._burl + str(req.json()['id']))

        for i in ["Bubology", long, "", None]:
            for ii in ["Great Me", long, "", None]:
                if i == "Bubology" and ii == "Great Me":
                    continue

                if not ((i == "Bubology" and ii is None) or (i is None and ii == "Great Me") or (i == ii is None)):
                    self.assertEqual(400, requests.put(self._burlid, {"title": i, "author": ii}).status_code)

                if i is not None and i is not None:
                    req = requests.post(self._burl, {"title": i, "author": ii})
                    self.assertEqual(400, req.status_code)


class RoleCRUD(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls._burl = 'http://pulse-rest-testing.herokuapp.com/books/'
        cls._bpush = {"title": "Bubology in heroes", "author": "Still Great Me"}
        cls._bres = requests.post(cls._burl, cls._bpush)
        cls._bid = str(cls._bres.json()['id'])
        cls._burlid = cls._burl + cls._bid
        cls._rurl = 'http://pulse-rest-testing.herokuapp.com/roles/'
        cls._rpush = {"name": "Bubolog Hero", "type": "Junior topotun", "level": 3, "book": cls._burlid}

    @classmethod
    def tearDownClass(cls) -> None:
        res = requests.get(cls._rurl)
        for i in res.json():
            if i["name"] == cls._rpush["name"]\
                    and i["type"] == cls._rpush["type"]\
                    and i["level"] == cls._rpush["level"]\
                    and i["book"] == cls._rpush["book"]:
                requests.delete(cls._rurl + str(i["id"]))

        res = requests.get(cls._burl)
        for i in res.json():
            if i["title"] == cls._bpush["title"] and i["author"] == cls._bpush["author"]:
                requests.delete(cls._burl + str(i["id"]))

    def setUp(self) -> None:
        self._rres = requests.post(self._rurl, self._rpush)
        self._rid = str(self._rres.json()['id'])
        self._rurlid = self._rurl + self._rid

    def tearDown(self) -> None:
        requests.delete(self._rurlid)

    def testCreateRole(self):
        self.assertEqual(201, self._rres.status_code)
        get = requests.get(self._rurlid).json()
        self.assertTrue(str(get["id"]) == str(self._rid) and
                        get["name"] == self._rpush["name"] and
                        get["type"] == self._rpush["type"] and
                        get["level"] == self._rpush["level"] and
                        get["book"] == self._rpush["book"])

    def testReadRoleNotBySID(self):
        self.assertTrue(f'"name":"{self._rpush["name"]}",'
                        f'"type":"{self._rpush["type"]}",'
                        f'"level":{self._rpush["level"]},'
                        f'"book":"{self._rpush["book"]}"'
                        in requests.get(self._rurl).text)

    def testUpdateRole(self):
        push = {"name": "New Bubolog Hero", "type": "God of topotun", "level": 800, "book": self._burlid}

        self.assertEqual(200, requests.put(self._rurlid, push).status_code)
        get = requests.get(self._rurlid)
        self.assertTrue(get.json()["name"] == push["name"]
                        and get.json()["type"] == push["type"]
                        and get.json()["level"] == push["level"]
                        and get.json()["book"] == push["book"])

        self.assertEqual(200, requests.put(self._rurlid, {"name": "Newest Bubolog Hero"}).status_code)
        self.assertEqual(200, requests.put(self._rurlid, {"type": "Just God"}).status_code)
        self.assertEqual(200, requests.put(self._rurlid, {"level": 9999999}).status_code)
        self.assertEqual(400, requests.put(self._rurlid, {"book": self._burl + '1'}).status_code)
        get = requests.get(self._rurlid)
        self.assertTrue(get.json()["name"] == "Newest Bubolog Hero"
                        and get.json()["type"] == "Just God"
                        and get.json()["level"] == 9999999
                        and get.json()["book"] == self._burlid)

    def testDeleteRole(self):
        requests.delete(self._rurlid)
        self.assertEqual(404, requests.get(self._rurlid).status_code)
        self.assertFalse(f'"id":{self._bid},"' in requests.get(self._rurl).text)

    # def testWrongRoleInput(self):
        # self.assertEqual(400, requests.post(self._burl, {"title": "Bubology"}).status_code)
        # self.assertEqual(415, requests.post(self._burl, "abc").status_code)
        # with self.assertRaises(TypeError):
        #     requests.post(self._burl, 100)
        # self.assertEqual(415, requests.put(self._burlid, "abc").status_code)
        # with self.assertRaises(TypeError):
        #     requests.put(self._burlid, 100)