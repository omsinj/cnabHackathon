
SEGMENT_B_SCHEMA = [
    {"name": "beneficiary_tax_id", "type": "num", "length": 14, "required": True},
    {"name": "address", "type": "alpha", "length": 35, "required": True},
    {"name": "address_number", "type": "num", "length": 5, "required": False},
    {"name": "address_complement", "type": "alpha", "length": 15, "required": False},
    {"name": "neighborhood", "type": "alpha", "length": 20, "required": False},
    {"name": "city", "type": "alpha", "length": 20, "required": True},
    {"name": "zip_code", "type": "num", "length": 5, "required": True},
    {"name": "zip_suffix", "type": "num", "length": 3, "required": True},
    {"name": "state", "type": "alpha", "length": 2, "required": True},
    {"name": "expiration_date", "type": "num", "length": 8, "required": False},
    {"name": "document_value", "type": "num", "length": 15, "required": False},
    {"name": "rebate", "type": "num", "length": 15, "required": False},
    {"name": "discount", "type": "num", "length": 15, "required": False},
    {"name": "interest", "type": "num", "length": 15, "required": False},
    {"name": "fine", "type": "num", "length": 15, "required": False},
]
