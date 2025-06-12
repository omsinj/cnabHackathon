SEGMENT_A_SCHEMA = [
    {"name": "payer_bank_code", "type": "num", "length": 3, "required": True},
    {"name": "payer_agency", "type": "num", "length": 4, "required": True},
    {"name": "payer_account", "type": "num", "length": 8, "required": True},
    {"name": "payer_name", "type": "alpha", "length": 29, "required": True},
    {"name": "company_ref", "type": "alpha", "length": 19, "required": False},
    {"name": "payment_date", "type": "num", "length": 8, "required": True},
    {"name": "currency_code", "type": "alpha", "length": 3, "required": True},
    {"name": "amount_currency", "type": "num", "length": 15, "required": False},
    {"name": "payment_amount", "type": "num", "length": 15, "required": True},
    {"name": "bank_ref", "type": "alpha", "length": 20, "required": False},
    {"name": "effective_date", "type": "num", "length": 8, "required": False},
    {"name": "effective_amount", "type": "num", "length": 15, "required": False},
    {"name": "ted_purpose_code", "type": "alpha", "length": 5, "required": False},
    {"name": "notice", "type": "num", "length": 1, "required": False},
]

