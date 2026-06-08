import json
import unittest
from datetime import datetime, timezone, date
from bson.objectid import ObjectId
from flask import Flask
from api_utils import MongoJSONEncoder  

class TestMongoJSONEncoder(unittest.TestCase):
    def setUp(self):
        self.app = Flask(__name__)
        self.app.json = MongoJSONEncoder(self.app)

    def test_encode_objectid(self):
        obj_id = ObjectId()
        result = self.app.json.dumps({'_id': obj_id})
        expected = f'{{"_id": "{str(obj_id)}"}}'
        self.assertEqual(result, expected)

    def test_encode_datetime(self):
        now = datetime.now(timezone.utc)
        result = self.app.json.dumps({'timestamp': now})
        expected = f'{{"timestamp": "{str(now)}"}}'
        self.assertEqual(result, expected)

    def test_encode_date(self):
        today = date.today()
        result = self.app.json.dumps({'today': today})
        expected = f'{{"today": "{str(today)}"}}'
        self.assertEqual(result, expected)

    def test_encode_custom_isoformat(self):
        class CustomISO:
            def isoformat(self):
                return "2024-06-25T12:34:56"
            def __str__(self):
                return self.isoformat()
        custom = CustomISO()
        result = self.app.json.dumps({'custom': custom})
        expected = '{"custom": "2024-06-25T12:34:56"}'
        self.assertEqual(result, expected)

    def test_encode_mixed_objects(self):
        obj_id = ObjectId()
        now = datetime.now(timezone.utc)
        data = {
            '_id': obj_id,
            'timestamp': now,
            'message': 'Test serialization'
        }
        result = self.app.json.dumps(data)
        expected = f'{{"_id": "{str(obj_id)}", "timestamp": "{str(now)}", "message": "Test serialization"}}'
        self.assertEqual(json.loads(result), json.loads(expected))

if __name__ == '__main__':
    unittest.main()

