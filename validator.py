from typing import Dict, List
import re

# --- Schema Imports ---
from schemas.file_header import FILE_HEADER_SCHEMA
from schemas.file_trailer import FILE_TRAILER_SCHEMA
from schemas.segment_a import SEGMENT_A_SCHEMA
from schemas.segment_b import SEGMENT_B_SCHEMA
from schemas.segment_c import SEGMENT_C_SCHEMA
from schemas.batch_trailer import BATCH_TRAILER_SCHEMA
from schemas.pix_batch_header import PIX_BATCH_HEADER_SCHEMA
from schemas.pix_segment_a import PIX_SEGMENT_A_SCHEMA
from schemas.pix_segment_b import PIX_SEGMENT_B_SCHEMA
from schemas.pix_segment_c import PIX_SEGMENT_C_SCHEMA
from schemas.pix_batch_trailer import PIX_BATCH_TRAILER_SCHEMA
from schemas.boletos_batch_header import BOLETOS_BATCH_HEADER_SCHEMA
from schemas.boletos_segment_j import BOLETOS_SEGMENT_J_SCHEMA
from schemas.boletos_segment_j52 import BOLETOS_SEGMENT_J52_SCHEMA
from schemas.boletos_batch_trailer import BOLETOS_BATCH_TRAILER_SCHEMA

# -----------------------------
# Generic Schema-Based Validator
# -----------------------------
def validate_schema(record: Dict[str, str], schema: List[Dict], context: str = "") -> List[str]:
    errors = []
    for field in schema:
        name = field["name"]
        value = record.get(name, "").strip()
        label = f"{context}.{name}"

        if field.get("required") and not value:
            errors.append(f"[{label}] Required field is missing.")
        elif field["type"] == "num" and not value.isdigit():
            errors.append(f"[{label}] Must be numeric.")
        elif field["type"] == "alpha" and not re.fullmatch(r"[A-Za-z\s]*", value):
            errors.append(f"[{label}] Must contain only letters.")
        elif "length" in field and len(value) != field["length"]:
            errors.append(f"[{label}] Must be {field['length']} characters long.")
    return errors

# -------------------
# Utility Validators
# -------------------
def is_valid_date(val: str) -> bool:
    return bool(re.fullmatch(r'\d{8}', val))

def is_valid_amount(val: str) -> bool:
    return val.isdigit()

def is_valid_cnpj(val: str) -> bool:
    return bool(re.fullmatch(r'\d{14}', val))

def clean_zip(zip_code: str, zip_suffix: str) -> str:
    return re.sub(r'[^0-9]', '', zip_code + zip_suffix)[:8]

def is_valid_zip(val: str) -> bool:
    return bool(re.fullmatch(r'\d{8}', val))

# -------------------
# Segment Validator
# -------------------
def validate_segment(segment: Dict, index: int) -> List[str]:
    errors = []
    code = segment.get("segment_type", "")
    fields = segment.get("fields", {})

    if code == 'A':
        errors += validate_schema(fields, SEGMENT_A_SCHEMA, context=f"Segment A #{index}")
        if not is_valid_date(fields.get("payment_date", "")):
            errors.append(f"[Segment A #{index}] Invalid payment date.")
        if not is_valid_amount(fields.get("payment_amount", "")):
            errors.append(f"[Segment A #{index}] Invalid payment amount.")

    elif code == 'B':
        errors += validate_schema(fields, SEGMENT_B_SCHEMA, context=f"Segment B #{index}")
        if not is_valid_cnpj(fields.get("beneficiary_tax_id", "")):
            errors.append(f"[Segment B #{index}] Invalid tax ID.")
        if not is_valid_zip(clean_zip(fields.get("zip_code", ""), fields.get("zip_suffix", ""))):
            errors.append(f"[Segment B #{index}] Invalid ZIP code.")

    elif code == 'C':
        errors += validate_schema(fields, SEGMENT_C_SCHEMA, context=f"Segment C #{index}")
        for key in ['ir_amount', 'iss_amount', 'iof_amount', 'inss_amount']:
            val = fields.get(key, "")
            if val and not is_valid_amount(val):
                errors.append(f"[Segment C #{index}] {key.replace('_', ' ').title()} is not a valid number.")

    elif code == 'J':
        errors += validate_schema(fields, BOLETOS_SEGMENT_J_SCHEMA, context=f"Segment J #{index}")
        if not fields.get("barcode", "").isdigit():
            errors.append(f"[Segment J #{index}] Invalid or missing barcode.")
        if not is_valid_amount(fields.get("payment_amount", "")):
            errors.append(f"[Segment J #{index}] Invalid payment amount.")

    elif code == 'J52':
        errors += validate_schema(fields, BOLETOS_SEGMENT_J52_SCHEMA, context=f"Segment J52 #{index}")
        if not is_valid_zip(fields.get("payer_zip", "")):
            errors.append(f"[Segment J52 #{index}] Invalid payer ZIP code.")

    return errors

# -----------------------------
# File-Level Validator
# -----------------------------
def validate_file_structure(parsed_data: Dict) -> List[str]:
    issues = []

    # File header/trailer
    issues += validate_schema(parsed_data.get("file_header", {}), FILE_HEADER_SCHEMA, context="FileHeader")
    issues += validate_schema(parsed_data.get("file_trailer", {}), FILE_TRAILER_SCHEMA, context="FileTrailer")

    # Segment-by-segment validation
    for batch_idx, batch in enumerate(parsed_data.get("batches", [])):
        segments = batch.get("segments", [])
        segment_types = [s.get("segment_type", "") for s in segments]

        for i, segment in enumerate(segments):
            issues.extend(validate_segment(segment, i + 1))

        # Business Rule: Segment A must be followed by Segment B
        for i, seg_type in enumerate(segment_types):
            if seg_type == 'A' and (i + 1 >= len(segment_types) or segment_types[i + 1] != 'B'):
                issues.append(f"[Batch #{batch_idx + 1}] Segment A at index {i} is not followed by Segment B.")

    return issues

# -----------------------------
# AI Explanation Generator
# -----------------------------
def explain_segment(segment: Dict) -> str:
    code = segment.get("segment_type")
    fields = segment.get("fields", {})

    if code == 'A':
        return f"Payment from {fields.get('payer_name', 'UNKNOWN')} for BRL {fields.get('payment_amount', 'N/A')} on {fields.get('payment_date', 'N/A')}."
    elif code == 'B':
        return f"Beneficiary located at {fields.get('address', 'UNKNOWN')}, ZIP {fields.get('zip_code', '')}-{fields.get('zip_suffix', '')}."
    elif code == 'C':
        return f"Includes deductions - IR: {fields.get('ir_amount', '0')}, INSS: {fields.get('inss_amount', '0')}."
    elif code == 'J':
        return f"Boleto with barcode {fields.get('barcode', 'N/A')} for BRL {fields.get('payment_amount', 'N/A')}."
    elif code == 'J52':
        return f"Payer {fields.get('payer_name', 'N/A')} at {fields.get('payer_address', 'N/A')}."
    elif code == 'N':
        return f"Non-barcoded document from {fields.get('beneficiary_name', 'N/A')} for BRL {fields.get('payment_amount', 'N/A')}."
    elif code == 'O':
        return f"Tax payment with barcode {fields.get('barcode', 'N/A')}."
    elif code == 'Z':
        return f"Authenticated using code {fields.get('auth_code', 'N/A')}."
    return "No explanation available."
