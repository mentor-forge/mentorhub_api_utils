import unittest
from bson import ObjectId
from datetime import datetime

from api_utils import encode_document

class TestEncodeProperties(unittest.TestCase):

    def setUp(self):
        """Re-initialize the config for each test."""
        self.maxDiff = None

    def test_simple_id_encode(self):
        id_string = "123456789012345678901234"
        id_prop = "the_id_property"
        document = {id_prop: id_string}
        encode_document(document, [id_prop], [])
        self.assertEqual(document[id_prop], ObjectId(id_string))

    def test_sub_document_id_encode(self):
        id_string = "123456789012345678901234"
        id_prop = "the_id"
        document = {"baseObject": {id_prop: id_string}}
        encode_document(document, [id_prop], [])
        sub_document = document["baseObject"]
        self.assertEqual(sub_document[id_prop], ObjectId(id_string))

    def test_list_id_encode(self):
        id_string1 = "123456789012345678901234"
        id_string2 = "000000000000000000000001"
        id_prop = "list_of_ids"
        document = {id_prop: [id_string1, id_string2]}
        encode_document(document, [id_prop], [])
        self.assertEqual(document[id_prop][0], ObjectId(id_string1))
        self.assertEqual(document[id_prop][1], ObjectId(id_string2))

    def test_list_document_id_encode(self):
        id_string1 = "123456789012345678901234"
        id_string2 = "000000000000000000000001"
        id_prop = "sub_object_id"
        list_prop = "list_of_objects"
        document = {list_prop: [{id_prop: id_string1}, {id_prop: id_string2}]}
        encode_document(document, [id_prop], [])
        self.assertEqual(document[list_prop][0][id_prop], ObjectId(id_string1))
        self.assertEqual(document[list_prop][1][id_prop], ObjectId(id_string2))

    def test_multiple_id_encode(self):
        id_string1 = "123456789012345678901234"
        id_string2 = "000000000000000000000001"
        document = {"propertyA": id_string1, "propertyB": id_string2}
        encode_document(document, ["propertyA", "propertyB"], [])
        self.assertEqual(document["propertyA"], ObjectId(id_string1))
        self.assertEqual(document["propertyB"], ObjectId(id_string2))

    def test_simple_date_encode(self):
        date_string = "2024-12-27T12:34:56.000Z"
        date_property = "prop_name"
        document = {date_property: date_string}
        encode_document(document, [], [date_property])
        self.assertEqual(document[date_property], datetime.fromisoformat(date_string))

    def test_sub_document_date_encode(self):
        date_string = "2024-12-27T12:34:56.000Z"
        date_property = "prop_name"
        document = {"object": {date_property: date_string}}
        encode_document(document, [], [date_property])
        self.assertEqual(document["object"][date_property], datetime.fromisoformat(date_string))

    def test_multiple_date_encode(self):
        date_string1 = "2000-01-23T12:34:56.000Z"
        date_string2 = "2009-10-11T12:34:56.000Z"
        document = {"propertyA": date_string1, "propertyB": date_string2}
        encode_document(document, [], ["propertyA", "propertyB"])
        self.assertEqual(document["propertyA"], datetime.fromisoformat(date_string1))
        self.assertEqual(document["propertyB"], datetime.fromisoformat(date_string2))

    def test_list_date_encode(self):
        date_string1 = "2000-01-23T01:23:45.000Z"
        date_string2 = "2009-10-11T12:34:56.000Z"
        list_prop = "list_of_dates"
        document = {list_prop: [date_string1, date_string2]}
        encode_document(document, [], [list_prop])
        self.assertEqual(document[list_prop][0], datetime.fromisoformat(date_string1))
        self.assertEqual(document[list_prop][1], datetime.fromisoformat(date_string2))

    def test_list_document_date_encode(self):
        date_string1 = "2000-01-23T01:23:45.000Z"
        date_string2 = "2009-10-11T12:34:56.000Z"
        list_prop = "list_of_objects"
        date_prop = "date_property"
        document = {list_prop: [{date_prop: date_string1}, {date_prop: date_string2}]}
        encode_document(document, [], [date_prop])
        self.assertEqual(document[list_prop][0][date_prop], datetime.fromisoformat(date_string1))
        self.assertEqual(document[list_prop][1][date_prop], datetime.fromisoformat(date_string2))

    def test_complexity(self):
        document = {
            "property1": 1,
            "property2": "someData",
            "base_id_property": "000000000000000000000001",
            "list_of_id": [
                "000000000000000000000001",
                "000000000000000000000002",
                "000000000000000000000003"
            ],
            "date_property": "2000-01-23T01:23:45.000Z",
            "list_of_dates": [
                "2009-10-11T12:34:56.000Z",
                "2009-11-11T11:11:11.000Z",
                "2009-12-12T12:12:12.000Z",
                "2010-01-01T01:01:01.000Z",                
            ],
            "list_of_objects": [
                {"id_property": "000000000000000000000004", "date_property": "2002-02-02T02:02:02.000Z" },
                {"id_property": "000000000000000000000005", "date_property": "2003-03-03T03:03:03.000Z" },
                {"id_property": "000000000000000000000006", "date_property": "2004-04-04T04:04:04.000Z" },
            ]
        }

        expected = {
            "property1": 1,
            "property2": "someData",
            "base_id_property": ObjectId("000000000000000000000001"),
            "list_of_id": [
                ObjectId("000000000000000000000001"),
                ObjectId("000000000000000000000002"),
                ObjectId("000000000000000000000003")
            ],
            "date_property": datetime.fromisoformat("2000-01-23T01:23:45.000Z"),
            "list_of_dates": [
                datetime.fromisoformat("2009-10-11T12:34:56.000Z"),
                datetime.fromisoformat("2009-11-11T11:11:11.000Z"),
                datetime.fromisoformat("2009-12-12T12:12:12.000Z"),
                datetime.fromisoformat("2010-01-01T01:01:01.000Z"),
            ],
            "list_of_objects": [
                {"id_property": ObjectId("000000000000000000000004"), "date_property": datetime.fromisoformat("2002-02-02T02:02:02.000Z") },
                {"id_property": ObjectId("000000000000000000000005"), "date_property": datetime.fromisoformat("2003-03-03T03:03:03.000Z") },
                {"id_property": ObjectId("000000000000000000000006"), "date_property": datetime.fromisoformat("2004-04-04T04:04:04.000Z") },
            ]
        }

        encode_document(document, ["base_id_property", "id_property", "list_of_id"], ["date_property", "list_of_dates"])
        self.assertEqual(document, expected)

    def test_polymorphic(self):
        document = {
            "name": "Test polymorphic list",   
            "polymorphic_list": [
                {
                    "id_property": "999999999999999999999999", 
                    "date_property": "2009-10-11T12:34:56.000Z"
                },
                "123456789012345678901234",
                [
                    "123456789012345678900000",
                    "123456789012345678900001",
                    "123456789012345678900002",
                    "123456789012345678900003"
                ]
            ]
        }

        expected = {
            "name": "Test polymorphic list",   
            "polymorphic_list": [
                {
                    "id_property": "999999999999999999999999", 
                    "date_property": "2009-10-11T12:34:56.000Z"
                    # Note that these will not encode - known limitation
                },
                ObjectId("123456789012345678901234"),
                [
                    ObjectId("123456789012345678900000"),
                    ObjectId("123456789012345678900001"),
                    ObjectId("123456789012345678900002"),
                    ObjectId("123456789012345678900003")
                ]
            ]
        }

        encode_document(document, ["polymorphic_list", "id_property"], ["date_property"])
        self.assertEqual(document, expected)
        
if __name__ == '__main__':
    unittest.main()

