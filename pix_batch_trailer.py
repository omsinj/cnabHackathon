PIX_BATCH_TRAILER_SCHEMA = [
    {"name": "bank_code", "start": 1, "end": 3, "type": "num"},
    {"name": "service_batch", "start": 4, "end": 7, "type": "num"},
    {"name": "record_type", "start": 8, "end": 8, "type": "num"},
    {"name": "cnab_1", "start": 9, "end": 17, "type": "alpha"},
    {"name": "batch_record_count", "start": 18, "end": 23, "type": "num"},
    {"name": "amount_sum", "start": 24, "end": 41, "type": "num"},
    {"name": "coin_quantity_sum", "start": 42, "end": 59, "type": "num"},
    {"name": "debit_notice_number", "start": 60, "end": 65, "type": "num"},
    {"name": "cnab_2", "start": 66, "end": 230, "type": "alpha"},
    {"name": "occurrences", "start": 231, "end": 240, "type": "alpha"},
]
