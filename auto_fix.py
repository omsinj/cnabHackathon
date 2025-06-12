from copy import deepcopy
from typing import Dict, List


def auto_fix(parsed_data: Dict) -> Dict:
    """
    Applies automatic fixes to parsed CNAB240 structure.
    Returns a modified copy of the input.
    """
    fixed_data = deepcopy(parsed_data)
    for batch in fixed_data.get("batches", []):
        segments = batch.get("segments", [])
        fixed_segments = []
        i = 0

        while i < len(segments):
            seg = segments[i]
            seg_type = seg.get("segment_type")

            fixed_segments.append(seg)

            # Auto-insert missing Segment B after Segment A
            if seg_type == "A":
                next_seg = segments[i + 1] if i + 1 < len(segments) else None
                if not next_seg or next_seg.get("segment_type") != "B":
                    fake_b = {
                        "segment_type": "B",
                        "label": "Auto-Inserted Segment B",
                        "raw": "",
                        "fields": {
                            "beneficiary_tax_id": "",
                            "address": "",
                            "zip_code": "00000",
                            "zip_suffix": "000",
                        }
                    }
                    fixed_segments.append(fake_b)

            i += 1

        batch["segments"] = fixed_segments

    return fixed_data


def describe_auto_fixes(original: Dict, fixed: Dict) -> List[str]:
    """
    Compare original and fixed and return human-readable list of what was fixed.
    """
    messages = []
    for batch_idx, (orig_batch, fixed_batch) in enumerate(zip(original.get("batches", []), fixed.get("batches", []))):
        orig_segments = orig_batch.get("segments", [])
        fixed_segments = fixed_batch.get("segments", [])

        if len(fixed_segments) > len(orig_segments):
            for i in range(len(orig_segments), len(fixed_segments)):
                added_seg = fixed_segments[i]
                messages.append(f"Inserted missing Segment {added_seg['segment_type']} after Segment A in Batch #{batch_idx + 1}.")

    return messages
