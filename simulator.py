def pad(value: str, length: int, align='right', filler='0'):
    """Pad a string to a fixed length."""
    if value is None:
        value = ''
    if align == 'right':
        return value.rjust(length, filler)
    return value.ljust(length, filler)


def build_segment_a(fields: dict) -> str:
    line = [' '] * 240
    line[13] = 'A'  # Segment code
    line[44:73] = list(pad(fields.get("payer_name", ""), 29, 'left', ' '))
    line[74:93] = list(pad(fields.get("company_ref", ""), 19))
    line[94:102] = list(fields.get("payment_date", "00000000"))
    line[102:105] = list(fields.get("currency_code", "BRL"))
    line[120:135] = list(pad(fields.get("payment_amount", "0"), 15))
    line[135:155] = list(pad(fields.get("bank_ref", ""), 20))
    line[155:163] = list(fields.get("effective_date", "00000000"))
    line[220:225] = list(fields.get("ted_purpose_code", ""))
    line[230:231] = list(fields.get("notice", "N"))
    return ''.join(line)


def build_segment_b(fields: dict) -> str:
    line = [' '] * 240
    line[13] = 'B'
    line[18:32] = list(pad(fields.get("beneficiary_tax_id", ""), 14))
    line[33:62] = list(pad(fields.get("address", ""), 29, 'left', ' '))
    line[63:68] = list(pad(fields.get("address_number", ""), 5))
    line[68:83] = list(pad(fields.get("address_complement", ""), 15))
    line[83:98] = list(pad(fields.get("neighborhood", ""), 15))
    line[98:118] = list(pad(fields.get("city", ""), 20))
    line[118:123] = list(pad(fields.get("zip_code", ""), 5))
    line[123:126] = list(pad(fields.get("zip_suffix", ""), 3))
    line[126:128] = list(fields.get("state", ""))
    return ''.join(line)


def build_segment_c(fields: dict) -> str:
    line = [' '] * 240
    line[13] = 'C'
    line[18:33] = list(pad(fields.get("ir_amount", "0"), 15))
    line[33:48] = list(pad(fields.get("iss_amount", "0"), 15))
    line[48:63] = list(pad(fields.get("iof_amount", "0"), 15))
    line[63:78] = list(pad(fields.get("deductions", "0"), 15))
    line[78:93] = list(pad(fields.get("additions", "0"), 15))
    line[113:128] = list(pad(fields.get("inss_amount", "0"), 15))
    return ''.join(line)


def regenerate_file(parsed: dict) -> list:
    """Reconstructs a CNAB240 .txt from parsed structured data."""
    lines = []

    # File Header (placeholder padding)
    file_header = parsed.get("file_header", {})
    header_line = pad("".join(str(v) for v in file_header.values()), 240)
    lines.append(header_line)

    for batch in parsed.get("batches", []):
        # Batch Header (placeholder padding)
        batch_header = batch.get("batch_header", {})
        batch_header_line = pad("".join(str(v) for v in batch_header.values()), 240)
        lines.append(batch_header_line)

        # Segments
        for segment in batch.get("segments", []):
            seg_type = segment.get("segment_type")
            fields = segment.get("fields", {})
            if seg_type == 'A':
                lines.append(build_segment_a(fields))
            elif seg_type == 'B':
                lines.append(build_segment_b(fields))
            elif seg_type == 'C':
                lines.append(build_segment_c(fields))
            else:
                lines.append(segment.get("raw", pad("", 240)))  # Fallback to raw or blank

        # Batch Trailer (placeholder padding)
        batch_trailer = batch.get("batch_trailer", {})
        batch_trailer_line = pad("".join(str(v) for v in batch_trailer.values()), 240)
        lines.append(batch_trailer_line)

    # File Trailer (placeholder padding)
    file_trailer = parsed.get("file_trailer", {})
    trailer_line = pad("".join(str(v) for v in file_trailer.values()), 240)
    lines.append(trailer_line)

    return lines
