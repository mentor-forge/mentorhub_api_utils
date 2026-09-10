import unittest
from bson import ObjectId
from datetime import datetime, timezone

from api_utils import decode_document


class TestDecodeProperties(unittest.TestCase):

    def setUp(self):
        self.maxDiff = None

    def test_simple_id_decode(self):
        id_string = "123456789012345678901234"
        id_prop = "the_id_property"
        document = {id_prop: ObjectId(id_string)}
        decode_document(document, [id_prop], [])
        self.assertEqual(document[id_prop], id_string)

    def test_auto_id_decode_without_properties(self):
        id_string = "123456789012345678901234"
        document = {"_id": ObjectId(id_string), "other_id": ObjectId(id_string)}
        decode_document(document)
        self.assertEqual(document["_id"], id_string)
        self.assertEqual(document["other_id"], id_string)

    def test_sub_document_id_decode(self):
        id_string = "123456789012345678901234"
        id_prop = "the_id"
        document = {"baseObject": {id_prop: ObjectId(id_string)}}
        decode_document(document, [id_prop], [])
        sub_document = document["baseObject"]
        self.assertEqual(sub_document[id_prop], id_string)

    def test_list_id_decode(self):
        id_string1 = "123456789012345678901234"
        id_string2 = "000000000000000000000001"
        id_prop = "list_of_ids"
        document = {id_prop: [ObjectId(id_string1), ObjectId(id_string2)]}
        decode_document(document, [id_prop], [])
        self.assertEqual(document[id_prop][0], id_string1)
        self.assertEqual(document[id_prop][1], id_string2)

    def test_list_document_id_decode(self):
        id_string1 = "123456789012345678901234"
        id_string2 = "000000000000000000000001"
        id_prop = "sub_object_id"
        list_prop = "list_of_objects"
        document = {
            list_prop: [
                {id_prop: ObjectId(id_string1)},
                {id_prop: ObjectId(id_string2)},
            ]
        }
        decode_document(document, [id_prop], [])
        self.assertEqual(document[list_prop][0][id_prop], id_string1)
        self.assertEqual(document[list_prop][1][id_prop], id_string2)

    def test_multiple_id_decode(self):
        id_string1 = "123456789012345678901234"
        id_string2 = "000000000000000000000001"
        document = {
            "propertyA": ObjectId(id_string1),
            "propertyB": ObjectId(id_string2),
        }
        decode_document(document, ["propertyA", "propertyB"], [])
        self.assertEqual(document["propertyA"], id_string1)
        self.assertEqual(document["propertyB"], id_string2)

    def test_simple_date_decode(self):
        dt = datetime(2024, 12, 27, 12, 34, 56, tzinfo=timezone.utc)
        date_property = "prop_name"
        document = {date_property: dt}
        decode_document(document, [], [date_property])
        self.assertEqual(document[date_property], dt.isoformat())

    def test_sub_document_date_decode(self):
        dt = datetime(2024, 12, 27, 12, 34, 56, tzinfo=timezone.utc)
        date_property = "prop_name"
        document = {"object": {date_property: dt}}
        decode_document(document, [], [date_property])
        self.assertEqual(document["object"][date_property], dt.isoformat())

    def test_extended_json_oid_decode(self):
        id_string = "507f1f77bcf86cd799439011"
        document = {"mentor_id": {"$oid": id_string}}
        decode_document(document)
        self.assertEqual(document["mentor_id"], id_string)

    def test_extended_json_date_decode(self):
        date_string = "2026-09-10T00:00:00.000Z"
        document = {"created_at": {"$date": date_string}}
        decode_document(document)
        self.assertEqual(document["created_at"], date_string)

    def test_list_of_documents_decode(self):
        id_string = "507f1f77bcf86cd799439011"
        docs = [
            {"_id": ObjectId(id_string), "name": "Item 1"},
            {"_id": ObjectId(id_string), "name": "Item 2"},
        ]
        decode_document(docs)
        self.assertEqual(docs[0]["_id"], id_string)
        self.assertEqual(docs[1]["_id"], id_string)

    def test_invalid_parameters(self):
        with self.assertRaises(ValueError):
            decode_document({}, "not-a-list", [])
        with self.assertRaises(ValueError):
            decode_document({}, [], "not-a-list")
