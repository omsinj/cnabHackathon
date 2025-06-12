import os
import json
from parser import parse_cnab240
from validator import validate_file_structure, explain_segment

def generate_examples(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = [line.strip() for line in f.readlines() if line.strip()]

    parsed = parse_cnab240(lines)
    issues = validate_file_structure(parsed)

    examples = []

    for batch in parsed.get("batches", []):
        for segment in batch.get("segments", []):
            raw = segment.get("raw", "")
            explanation = explain_segment(segment)
            examples.append({
                "input": raw,
                "fix": explanation
            })

    return examples

# 👇 Point to a folder of CNAB240 .txt files
cnab_folder = "sample_cnab_files"
all_examples = []

for filename in os.listdir(cnab_folder):
    if filename.endswith(".txt"):
        path = os.path.join(cnab_folder, filename)
        examples = generate_examples(path)
        all_examples.extend(examples)

with open("training_data.json", "w", encoding="utf-8") as f:
    json.dump(all_examples, f, indent=2, ensure_ascii=False)

print(f"✅ Saved {len(all_examples)} examples to training_data.json")



import os
from parser import parse_cnab240

data_dir = "sample_files"
output = []

for file in os.listdir(data_dir):
    if not file.endswith(".txt"):
        continue
    with open(os.path.join(data_dir, file), "r", encoding="utf-8") as f:
        lines = f.readlines()

    for line in lines:
        label = line[13] if line[7] == '3' else line[7]  # Segment or Record Type
        features = {
            "line": line.strip(),
            "length": len(line),
            "digit_7": line[7],
            "digit_13": line[13] if len(line) > 13 else '',
            "label": label
        }
        output.append(features)

# Save to CSV
import pandas as pd
df = pd.DataFrame(output)
df.to_csv("training_data.csv", index=False)
