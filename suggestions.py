from typing import List, Dict


def suggest_fixes(parsed_data: Dict) -> List[str]:
    suggestions = []

    for batch in parsed_data.get("batches", []):
        for idx, segment in enumerate(batch.get("segments", [])):
            if segment.get("segment_type") == "B":
                fields = segment.get("fields", {})
                zip_code = fields.get("zip_code", "")
                zip_suffix = fields.get("zip_suffix", "")
                full_zip = (zip_code + zip_suffix).strip()

                # Suggest fix if ZIP is malformed (contains non-digits or wrong length)
                if not full_zip.isdigit() or len(full_zip) != 8:
                    suggestions.append(
                        f"[Segment B #{idx + 1}] Suggest fixing malformed ZIP code: {full_zip}"
                    )

    return suggestions
