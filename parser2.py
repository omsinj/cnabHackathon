from typing import List, Dict
import joblib
import pandas as pd

# Constants based on CNAB240 spec
SEGMENT_MAP = {
    'A': 'Segment A - Payment Info',
    'A00': 'Segment A00 - Payment Initiation',
    'B': 'Segment B - Beneficiary Details',
    'C': 'Segment C - Taxes/Deductions',
    'J': 'Segment J - Boleto Info',
    'J52': 'Segment J52 - Boleto Extra Info',
    'N': 'Segment N - Non-Barcoded Tax',
    'O': 'Segment O - Barcoded Tax',
    'Z': 'Segment Z - Authentication'
}

RECORD_TYPE_POS = 7
SEGMENT_CODE_POS = 13

# ------------------------------
# AI-Powered Segment Classifier
# ------------------------------
def predict_segment_type(line: str) -> str:
    try:
        model = joblib.load("models/segment_classifier.pkl")
        le = joblib.load("models/segment_label_encoder.pkl")

        features = {
            "length": len(line),
            "record_type": line[RECORD_TYPE_POS] if len(line) > RECORD_TYPE_POS else "",
            "segment_code": line[SEGMENT_CODE_POS] if len(line) > SEGMENT_CODE_POS else "",
            "digit_count": sum(c.isdigit() for c in line),
            "alpha_count": sum(c.isalpha() for c in line),
            "space_count": sum(c.isspace() for c in line),
        }

        X = pd.DataFrame([features])
        y_pred = model.predict(X)
        return le.inverse_transform(y_pred)[0]
    except Exception as e:
        return "UNK"  # fallback

# ------------------------------
# Main Parsing Function
# ------------------------------
def parse_cnab240(lines: List[str]) -> Dict:
    data = {
        "file_header": {},
        "batches": [],
        "file_trailer": {}
    }

    current_batch = None

    for line in lines:
        record_type = line[RECORD_TYPE_POS]

        if record_type == '0':
            data['file_header'] = parse_header(line)

        elif record_type == '1':
            current_batch = {
                "batch_header": parse_batch_header(line),
                "segments": [],
                "batch_trailer": {}
            }
            data['batches'].append(current_batch)

        elif record_type == '3':
            segment_code = line[SEGMENT_CODE_POS:SEGMENT_CODE_POS+3].strip()
            if not segment_code or segment_code == '':
                segment_code = predict_segment_type(line)
            segment = parse_segment(line, segment_code)
            current_batch['segments'].append(segment)

        elif record_type == '5':
            current_batch['batch_trailer'] = parse_batch_trailer(line)

        elif record_type == '9':
            data['file_trailer'] = parse_file_trailer(line)

    return data

# ------------------------------
# Parsers for Line Types
# ------------------------------
def parse_header(line: str) -> Dict:
    return {
        "bank_code": line[0:3],
        "company_name": line[72:102].strip(),
        "generation_date": line[143:151],
        "layout_version": line[164:167],
    }

def parse_batch_header(line: str) -> Dict:
    return {
        "operation_type": line[8],
        "service_type": line[9:11],
        "company_name": line[72:102].strip(),
    }

def parse_batch_trailer(line: str) -> Dict:
    return {
        "record_count": line[17:23].strip(),
        "sum_amounts": line[23:41].strip(),
    }

def parse_file_trailer(line: str) -> Dict:
    return {
        "batch_count": line[17:23].strip(),
        "total_records": line[23:29].strip(),
    }

def parse_segment(line: str, code: str) -> Dict:
    label = SEGMENT_MAP.get(code, f"Unknown Segment {code}")
    return {
        "segment_type": code,
        "label": label,
        "raw": line,
        "fields": extract_fields(line, code)
    }

# ------------------------------
# Field Extractors by Segment
# ------------------------------
def extract_fields(line: str, code: str) -> Dict:
    if code in ['A00', 'A']:
        return {
            "payer_bank_code": line[0:3],
            "payer_agency": line[17:21].strip(),
            "payer_account": line[23:31].strip(),
            "payer_name": line[44:73].strip(),
            "company_ref": line[74:93].strip(),
            "payment_date": line[94:102].strip(),
            "currency_code": line[102:105].strip(),
            "amount_currency": line[105:120].strip(),
            "payment_amount": line[120:135].strip(),
            "bank_ref": line[135:155].strip(),
            "effective_date": line[155:163].strip(),
            "effective_amount": line[163:178].strip(),
            "ted_purpose_code": line[220:225].strip() if len(line) > 225 else "",
            "notice": line[230:231].strip() if len(line) > 230 else "",
        }

    elif code == 'B':
        return {
            "beneficiary_tax_id": line[18:32].strip(),
            "address": line[33:62].strip(),
            "address_number": line[63:68].strip(),
            "address_complement": line[68:83].strip(),
            "neighborhood": line[83:98].strip(),
            "city": line[98:118].strip(),
            "zip_code": line[118:123].strip(),
            "zip_suffix": line[123:126].strip(),
            "state": line[126:128].strip(),
            "expiration_date": line[128:136].strip(),
            "document_value": line[136:151].strip(),
            "rebate": line[151:166].strip(),
            "discount": line[166:181].strip(),
            "interest": line[181:196].strip(),
            "fine": line[196:211].strip(),
        }

    elif code == 'C':
        return {
            "ir_amount": line[18:33].strip(),
            "iss_amount": line[33:48].strip(),
            "iof_amount": line[48:63].strip(),
            "deductions": line[63:78].strip(),
            "additions": line[78:93].strip(),
            "inss_amount": line[113:128].strip(),
        }

    elif code == 'J':
        return {
            "barcode": line[18:62].strip(),
            "assignor": line[62:92].strip(),
            "due_date": line[92:100].strip(),
            "nominal_amount": line[100:115].strip(),
            "discount": line[115:130].strip(),
            "fine": line[130:145].strip(),
            "payment_date": line[145:153].strip(),
            "payment_amount": line[153:168].strip(),
            "document_number": line[183:203].strip(),
            "bank_ref": line[203:223].strip(),
        }

    elif code == 'J52':
        return {
            "payer_enrollment_type": line[20:21].strip(),
            "payer_enrollment_number": line[21:35].strip(),
            "payer_name": line[36:75].strip(),
            "payer_address": line[76:115].strip(),
            "payer_city": line[116:130].strip(),
            "payer_zip": line[131:136].strip(),
            "payer_state": line[138:140].strip(),
        }

    elif code == 'N':
        return {
            "document_number": line[18:34].strip(),
            "beneficiary_name": line[34:74].strip(),
            "payment_amount": line[74:89].strip(),
            "payment_date": line[89:97].strip(),
            "bank_ref": line[97:117].strip(),
        }

    elif code == 'O':
        return {
            "barcode": line[18:62].strip(),
            "document_number": line[62:82].strip(),
            "due_date": line[82:90].strip(),
            "nominal_value": line[90:105].strip(),
            "payment_date": line[105:113].strip(),
            "payment_amount": line[113:128].strip(),
        }

    elif code == 'Z':
        return {
            "auth_code": line[18:58].strip(),
        }

    else:
        return {
            "note": f"Segment {code} not yet mapped."
        }
