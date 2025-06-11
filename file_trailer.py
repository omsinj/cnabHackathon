file_trailer_schema = [
    {"name": "bank_code", "start": 1, "end": 3, "length": 3, "type": "num", "required": True},
    {"name": "service_batch", "start": 4, "end": 7, "length": 4, "type": "num", "required": True},
    {"name": "record_type", "start": 8, "end": 8, "length": 1, "type": "num", "required": True},
    {"name": "cnab", "start": 9, "end": 17, "length": 9, "type": "alpha", "required": False},
    {"name": "batch_count", "start": 18, "end": 23, "length": 6, "type": "num", "required": True},
    {"name": "record_count", "start": 24, "end": 29, "length": 6, "type": "num", "required": True},
    {"name": "account_count", "start": 30, "end": 35, "length": 6, "type": "num", "required": True},
]
