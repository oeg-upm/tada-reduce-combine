from time import sleep
import os
import unittest
import json
from app import app
from app import UPLOAD_DIR
from models import create_tables, get_database, Bite, Apple, STATUS_COMPLETE, STATUS_NEW

database = get_database()

sleep_time = 1  # in seconds


class CombineTest(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        create_tables()

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        # creates a test client
        self.app = app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True
        app.testing = True

    def tearDown(self):
        pass

    def test_pages_status_code(self):
        result = self.app.get('/')
        self.assertEqual(result.status_code, 200)

        result = self.app.get('/list_bites')
        self.assertEqual(result.status_code, 200)

        result = self.app.get('/list')
        self.assertEqual(result.status_code, 200)

    def test_add_bite(self):
        fname = "test_volleyball_1.json"
        fdir = os.path.join("tests", fname)
        f = open(fdir)
        table_name = "volleyball_single"
        table_col = 0
        data = {'table': table_name, 'column': table_col, 'slice': 0, 'total': 1, 'm': 3}
        data['graph'] = (f, "volleyball.csv")
        Bite.delete().execute()  # delete all Bites
        Apple.delete().execute()  # delete all Apples
        result = self.app.post('/add', data=data, content_type='multipart/form-data')
        self.assertEqual(result.status_code, 200, msg=result.data)
        database.connect(reuse_if_open=True)
        self.assertEqual(len(Bite.select()), 1)
        sleep(sleep_time)
        result = self.app.get('/status')
        self.assertEqual(result.status_code, 200, msg=result.data)
        self.assertTrue(result.is_json)
        j = {
            "apples": [

                {
                    "apple": table_name,
                    "status": STATUS_COMPLETE,
                    "complete": True
                }
            ]
        }
        self.assertDictEqual(result.get_json(), j)
        apple = Apple.select().where(Apple.table==table_name, Apple.column==table_col)[0]
        f = open(os.path.join(UPLOAD_DIR, apple.fname))
        merge_graph = json.load(f)
        target_uri = "http://dbpedia.org/ontology/VolleyballPlayer"
        self.assertEqual(merge_graph[target_uri]["Lc"], 0.5)
        f.close()

        result = self.app.get('/list')
        j = result.json
        apples = j['apples']
        self.assertEqual(len(apples), 1)
        j_apple = apples[0]
        result = self.app.get('/get_graph?id='+str(j_apple["id"]))
        self.assertEqual(200, result.status_code, msg=result.data)

    def test_add_multiple_bite(self):
        fname = "test_volleyball_1.json"
        fdir = os.path.join("tests", fname)
        f = open(fdir)
        table_name = "volleyball_double"
        table_col = 0
        data = {'table': table_name, 'column': table_col, 'slice': 0, 'total': 2, 'm': 3}
        data['graph'] = (f, "volleyball.csv")
        Bite.delete().execute()  # delete all Bites
        Apple.delete().execute()  # delete all Apples
        result = self.app.post('/add', data=data, content_type='multipart/form-data')
        self.assertEqual(result.status_code, 200, msg=result.data)
        database.connect(reuse_if_open=True)
        self.assertEqual(len(Bite.select()), 1)
        sleep(sleep_time)
        result = self.app.get('/status')
        self.assertEqual(result.status_code, 200, msg=result.data)
        self.assertTrue(result.is_json)
        j = {
            "apples": [
                {
                    "apple": table_name,
                    "status": STATUS_NEW,
                    "complete": False
                }
            ]
        }
        self.assertDictEqual(result.get_json(), j)
        fname = "test_volleyball_2.json"
        fdir = os.path.join("tests", fname)
        f = open(fdir)
        data = {'table': table_name, 'column': table_col, 'slice': 1, 'total': 2, 'm': 3}
        data['graph'] = (f, "volleyball.csv")
        result = self.app.post('/add', data=data, content_type='multipart/form-data')
        self.assertEqual(result.status_code, 200, msg=result.data)
        database.connect(reuse_if_open=True)
        self.assertEqual(len(Bite.select()), 2)
        sleep(sleep_time)
        result = self.app.get('/status')
        self.assertEqual(result.status_code, 200, msg=result.data)
        self.assertTrue(result.is_json)
        j = {
            "apples": [
                {
                    "apple": table_name,
                    "status": STATUS_COMPLETE,
                    "complete": True
                }
            ]
        }
        self.assertDictEqual(result.get_json(), j)
        apple = Apple.select().where(Apple.table==table_name, Apple.column==table_col)[0]
        f = open(os.path.join(UPLOAD_DIR, apple.fname))
        merge_graph = json.load(f)
        target_uri = "http://dbpedia.org/ontology/VolleyballPlayer"
        self.assertEqual(merge_graph[target_uri]["Lc"], 0.9)  # 0.5 + 0.4
        f.close()

    def test_add_multiple_incomplete_bite(self):
        fname = "test_volleyball_1.json"
        fdir = os.path.join("tests", fname)
        f = open(fdir)
        table_name = "volleyball_double"
        data = {'table': table_name, 'column': 0, 'slice': 0, 'total': 3, 'm': 3}
        data['graph'] = (f, "volleyball.csv")
        Bite.delete().execute()  # delete all Bites
        Apple.delete().execute()  # delete all Apples
        result = self.app.post('/add', data=data, content_type='multipart/form-data')
        self.assertEqual(result.status_code, 200, msg=result.data)
        database.connect(reuse_if_open=True)
        self.assertEqual(len(Bite.select()), 1)
        sleep(sleep_time)
        result = self.app.get('/status')
        self.assertEqual(result.status_code, 200, msg=result.data)
        self.assertTrue(result.is_json)
        j = {
            "apples": [
                {
                    "apple": table_name,
                    "status": STATUS_NEW,
                    "complete": False

                }
            ]
        }
        self.assertDictEqual(result.get_json(), j)
        fname = "test_volleyball_1.json"
        fdir = os.path.join("tests", fname)
        f = open(fdir)
        data = {'table': table_name, 'column': 0, 'slice': 1, 'total': 3, 'm': 3}
        data['graph'] = (f, "volleyball.csv")
        result = self.app.post('/add', data=data, content_type='multipart/form-data')
        self.assertEqual(result.status_code, 200, msg=result.data)
        database.connect(reuse_if_open=True)
        self.assertEqual(len(Bite.select()), 2)
        sleep(sleep_time)
        result = self.app.get('/status')
        self.assertEqual(result.status_code, 200, msg=result.data)
        self.assertTrue(result.is_json)
        j = {
            "apples": [
                {
                    "apple": table_name,
                    "status": STATUS_NEW,
                    "complete": False
                }
            ]
        }
        self.assertDictEqual(result.get_json(), j)
