# serialization.py slave

from datetime import datetime

class DataSerializer:
    """Handles data serialization and deserialization."""
    @staticmethod
    def serialize(data):
        serialized = []
        for record in data:
            serialized_record = {}
            for key, value in record.items():
                if isinstance(value, datetime):
                    serialized_record[key] = value.isoformat()
                else:
                    serialized_record[key] = value
            serialized.append(serialized_record)
        return serialized
