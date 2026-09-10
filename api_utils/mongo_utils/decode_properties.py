from datetime import date, datetime
from bson import ObjectId


def decode_document(document, id_properties=None, date_properties=None):
    """Decode ObjectId and datetime values from MongoDB in place.

    This function traverses the given document recursively, modifying it in place.
    It decodes BSON types into JSON-serializable Python primitives:
    - ``ObjectId`` instances are converted to strings.
    - ``datetime`` and ``date`` instances are converted to ISO 8601 strings.
    - MongoDB Extended JSON dicts (``{"$oid": "..."}`` and ``{"$date": "..."}``)
      are unwrapped to strings.

    If ``id_properties`` or ``date_properties`` are provided, they must be lists of strings.
    If omitted or None, all encountered ``ObjectId``, ``datetime``, ``date``, and Extended JSON
    dict values are decoded automatically.

    Args:
        document (dict or list): The document or list of documents to decode in place.
        id_properties (list of str, optional): Keys expected to be IDs to convert to str.
        date_properties (list of str, optional): Keys expected to be dates to convert to ISO string.

    Returns:
        dict or list: The modified document.

    Raises:
        ValueError: If id_properties or date_properties are provided but not lists of strings,
                    or if an element cannot be decoded.
    """
    if id_properties is not None:
        if not isinstance(id_properties, list) or not all(
            isinstance(prop, str) for prop in id_properties
        ):
            raise ValueError("id_properties must be a list of strings")
    if date_properties is not None:
        if not isinstance(date_properties, list) or not all(
            isinstance(prop, str) for prop in date_properties
        ):
            raise ValueError("date_properties must be a list of strings")

    def decode_value(key, value):
        try:
            if isinstance(value, dict):
                if "$oid" in value and len(value) == 1:
                    return str(value["$oid"])
                if "$date" in value and len(value) == 1:
                    return str(value["$date"])
                return value

            is_id = (id_properties is not None and key in id_properties) or isinstance(
                value, ObjectId
            )
            if is_id and isinstance(value, ObjectId):
                return str(value)

            is_date = (
                date_properties is not None and key in date_properties
            ) or isinstance(value, (datetime, date))
            if is_date and isinstance(value, (datetime, date)):
                return value.isoformat()

            if isinstance(value, list):
                return [decode_value(key, item) for item in value]

            return value
        except Exception as e:
            raise ValueError(f"Error decoding key '{key}': {value}") from e

    def _traverse(node):
        if isinstance(node, dict):
            for k, v in list(node.items()):
                if isinstance(v, dict):
                    if "$oid" in v and len(v) == 1:
                        node[k] = str(v["$oid"])
                    elif "$date" in v and len(v) == 1:
                        node[k] = str(v["$date"])
                    else:
                        _traverse(v)
                elif isinstance(v, list):
                    if all(isinstance(item, dict) for item in v):
                        for item in v:
                            _traverse(item)
                    else:
                        node[k] = [decode_value(k, item) for item in v]
                else:
                    node[k] = decode_value(k, v)
        elif isinstance(node, list):
            for idx, item in enumerate(node):
                if isinstance(item, (dict, list)):
                    _traverse(item)
                else:
                    node[idx] = decode_value(None, item)
        return node

    return _traverse(document)
