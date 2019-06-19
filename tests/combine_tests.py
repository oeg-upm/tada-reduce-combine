import os
import unittest

from app import app
from models import create_tables, database, Bite, Apple


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

    def tearDown(self):
        pass

    def test_pages_status_code(self):
        # sends HTTP GET request to the application
        # on the specified path
        result = self.app.get('/')
        # assert the status code of the response
        self.assertEqual(result.status_code, 200)

        result = self.app.get('/reason')
        self.assertEqual(result.status_code, 200)

        result = self.app.get('/list')
        self.assertEqual(result.status_code, 200)

    def test_add_bite(self):
        fname = "test_volleyball_1.json"
        fdir = os.path.join("tests", fname)
        f = open(fdir)
        table_name = "volleyball_single"
        data = {'table': table_name, 'column': 0, 'slice': 0, 'total': 1, 'm': 3}
        data['file_slice'] = (f, "volleyball.csv")
        Bite.delete().execute()  # delete all Bites
        Apple.delete().execute()  # delete all Apples
        result = self.app.post('/add', data=data, content_type='multipart/form-data')
        self.assertEqual(result.status_code, 200, msg=result.data)
        database.connect(reuse_if_open=True)
        self.assertEqual(len(Bite.select()), 1)

        result = self.app.get('/status')
        self.assertEqual(result.status_code, 200, msg=result.data)
        self.assertTrue(result.is_json)
        j = {
            "apples": [

                {
                    "apple": table_name,
                    "status": "complete"
                }
            ]
        }
        self.assertDictEqual(result.get_json(), j)

    def test_add_multiple_bite(self):
        fname = "test_volleyball_1.json"
        fdir = os.path.join("tests", fname)
        f = open(fdir)
        table_name = "volleyball_double"
        data = {'table': table_name, 'column': 0, 'slice': 0, 'total': 2, 'm': 3}
        data['file_slice'] = (f, "volleyball.csv")
        Bite.delete().execute()  # delete all Bites
        Apple.delete().execute()  # delete all Apples
        result = self.app.post('/add', data=data, content_type='multipart/form-data')
        self.assertEqual(result.status_code, 200, msg=result.data)
        database.connect(reuse_if_open=True)
        self.assertEqual(len(Bite.select()), 1)
        result = self.app.get('/status')
        self.assertEqual(result.status_code, 200, msg=result.data)
        self.assertTrue(result.is_json)
        j = {
            "apples": [
                {
                    "apple": table_name,
                    "status": "missing"
                }
            ]
        }
        self.assertDictEqual(result.get_json(), j)
        fname = "test_volleyball_2.json"
        fdir = os.path.join("tests", fname)
        f = open(fdir)
        data = {'table': table_name, 'column': 0, 'slice': 1, 'total': 2, 'm': 3}
        data['file_slice'] = (f, "volleyball.csv")
        result = self.app.post('/add', data=data, content_type='multipart/form-data')
        self.assertEqual(result.status_code, 200, msg=result.data)
        database.connect(reuse_if_open=True)
        self.assertEqual(len(Bite.select()), 2)
        result = self.app.get('/status')
        self.assertEqual(result.status_code, 200, msg=result.data)
        self.assertTrue(result.is_json)
        j = {
            "apples": [
                {
                    "apple": table_name,
                    "status": "complete"
                }
            ]
        }
        self.assertDictEqual(result.get_json(), j)

    def test_add_multiple_incomplete_bite(self):
        fname = "test_volleyball_1.json"
        fdir = os.path.join("tests", fname)
        f = open(fdir)
        table_name = "volleyball_double"
        data = {'table': table_name, 'column': 0, 'slice': 0, 'total': 3, 'm': 3}
        data['file_slice'] = (f, "volleyball.csv")
        Bite.delete().execute()  # delete all Bites
        Apple.delete().execute()  # delete all Apples
        result = self.app.post('/add', data=data, content_type='multipart/form-data')
        self.assertEqual(result.status_code, 200, msg=result.data)
        database.connect(reuse_if_open=True)
        self.assertEqual(len(Bite.select()), 1)
        result = self.app.get('/status')
        self.assertEqual(result.status_code, 200, msg=result.data)
        self.assertTrue(result.is_json)
        j = {
            "apples": [
                {
                    "apple": table_name,
                    "status": "missing"
                }
            ]
        }
        self.assertDictEqual(result.get_json(), j)
        fname = "test_volleyball_1.json"
        fdir = os.path.join("tests", fname)
        f = open(fdir)
        data = {'table': table_name, 'column': 0, 'slice': 1, 'total': 3, 'm': 3}
        data['file_slice'] = (f, "volleyball.csv")
        result = self.app.post('/add', data=data, content_type='multipart/form-data')
        self.assertEqual(result.status_code, 200, msg=result.data)
        database.connect(reuse_if_open=True)
        self.assertEqual(len(Bite.select()), 2)
        result = self.app.get('/status')
        self.assertEqual(result.status_code, 200, msg=result.data)
        self.assertTrue(result.is_json)
        j = {
            "apples": [
                {
                    "apple": table_name,
                    "status": "missing"
                }
            ]
        }
        self.assertDictEqual(result.get_json(), j)
