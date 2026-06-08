from datetime import datetime
from bson import ObjectId

def encode_document(document, id_properties, date_properties):
    """Encode ObjectId and datetime values for MongoDB in place.

    This function traverses the given document recursively, modifying it in place.
    It encodes specified fields for MongoDB: ``ObjectId`` for ``id_properties``
    and ``datetime`` for ``date_properties``.

    Args:
        document (dict): The document to encode. This is modified in place.
        id_properties (list): List of keys that should be converted to ObjectId.
        date_properties (list): List of keys that should be converted to datetime.

    Raises:
        ValueError: If id_properties or date_properties are not lists of strings,
                    or if a value in the document cannot be encoded.
    """
    # Validate inputs
    if not isinstance(id_properties, list) or not all(isinstance(prop, str) for prop in id_properties):
        raise ValueError("id_properties must be a list of strings")
    if not isinstance(date_properties, list) or not all(isinstance(prop, str) for prop in date_properties):
        raise ValueError("date_properties must be a list of strings")

    def encode_value(key, value):
        """Encode identified values."""
        try:
            if key in id_properties:
                if isinstance(value, str):
                    return ObjectId(value)
                if isinstance(value, list):
                    return [ObjectId(item) if isinstance(item, str) else item for item in value]
            if key in date_properties:
                if isinstance(value, str):
                    return datetime.fromisoformat(value)
                if isinstance(value, list):
                    return [datetime.fromisoformat(item) if isinstance(item, str) else item for item in value]
        except Exception as e:
            raise ValueError(f"Error encoding key '{key}': {value}") from e
        return value

    # Modify the document in place
    for key, value in document.items():
        if isinstance(value, dict):
            encode_document(value, id_properties, date_properties)  # Recursively modify nested dictionaries
        elif isinstance(value, list):
            if all(isinstance(item, dict) for item in value):
                for idx, item in enumerate(value):
                    encode_document(item, id_properties, date_properties)  # Recursively modify each nested dict in the list
            else:
                document[key] = [encode_value(key, item) for item in value]
        else:
            document[key] = encode_value(key, value)

    return document

