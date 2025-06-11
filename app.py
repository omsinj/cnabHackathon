import streamlit as st
from parser import parse_cnab240
from validator import validate_file_structure
from simulator import regenerate_file
from suggestions import suggest_fixes

# --------------------
# AI Explanation Helper
# --------------------
def explain_segment(segment):
    seg_type = segment.get("segment_type")
    f = segment.get("fields", {})

    if seg_type in ["A", "A00"]:
        return (
            f"Initiates a payment of BRL {f.get('payment_amount', 'N/A')} "
            f"to {f.get('payer_name', 'UNKNOWN')} on {f.get('payment_date', 'N/A')}."
        )
    elif seg_type == "B":
        zip_full = f"{f.get('zip_code', '')}-{f.get('zip_suffix', '')}".strip("-")
        return (
            f"Beneficiary in {f.get('city', 'UNKNOWN')} (ZIP {zip_full}), "
            f"Tax ID: {f.get('beneficiary_tax_id', 'N/A')}."
        )
    elif seg_type == "C":
        return (
            f"Deductions - IR: {f.get('ir_amount', '0')}, ISS: {f.get('iss_amount', '0')}, "
            f"INSS: {f.get('inss_amount', '0')}."
        )
    elif seg_type == "J":
        return (
            f"Boleto due on {f.get('due_date', 'N/A')} for BRL {f.get('nominal_amount', '0')}. "
            f"Assignor: {f.get('assignor', 'N/A')}."
        )
    elif seg_type == "J52":
        return (
            f"Payer: {f.get('payer_name', 'N/A')}, Final Beneficiary: {f.get('final_name', 'N/A')}."
        )
    elif seg_type == "N":
        return (
            f"Non-barcoded tax document for BRL {f.get('payment_amount', '0')} by "
            f"{f.get('beneficiary_name', 'N/A')}."
        )
    elif seg_type == "O":
        return (
            f"Barcoded tax payment with barcode {f.get('barcode', 'N/A')}, "
            f"amount BRL {f.get('payment_amount', 'N/A')}."
        )
    elif seg_type == "Z":
        return f"Authentication code: {f.get('auth_code', 'N/A')}."

    return "Explanation not available for this segment."

# -----------------------
# Scoring Quality Heuristic
# -----------------------
def compute_quality_score(errors: list, suggestions: list) -> int:
    deductions = len(errors) * 5 + len(suggestions) * 2
    return max(100 - deductions, 0)

# ------------------------
# Segment Visual Formatter
# ------------------------
def display_segment(segment, idx):
    st.subheader(f"Segment {segment['segment_type']} - #{idx + 1}")
    st.json(segment["fields"])
    st.caption(f"📄 Raw Line: `{segment['raw']}`")
    st.markdown(f"🧠 Explanation: *{explain_segment(segment)}*")
    st.markdown("---")

# ------------------------
# Streamlit App Entry Point
# ------------------------
def main():
    st.set_page_config(page_title="CNAB240 Analyzer", layout="wide")
    st.title("📄 CNAB240 AI-Powered Parser & Validator")

    uploaded_file = st.file_uploader("Upload a CNAB240 .txt file", type="txt")

    if uploaded_file:
        lines = [line.decode("utf-8").strip("\n") for line in uploaded_file.readlines()]
        parsed = parse_cnab240(lines)
        errors = validate_file_structure(parsed)
        suggestions = suggest_fixes(parsed)

        st.success("✅ File parsed successfully.")

        if errors:
            st.error("⚠️ Validation Issues:")
            for err in errors:
                st.markdown(f"- {err}")
        else:
            st.info("✅ No structural issues found.")

        if suggestions:
            st.warning("💡 Suggestions for Improvement:")
            for fix in suggestions:
                st.markdown(f"- {fix}")
        else:
            st.success("✅ No AI suggestions needed.")

        score = compute_quality_score(errors, suggestions)
        st.metric("📊 File Quality Score", f"{score}/100")

        if st.button("🔧 Auto-Apply Fixes"):
            st.info("Auto-fix logic placeholder. Fixing pipeline in development.")

        if st.button("📤 Generate & Download .txt File"):
            new_lines = regenerate_file(parsed)
            cnab_text = "\n".join(new_lines)
            st.download_button("⬇️ Download Corrected CNAB240", cnab_text, file_name="corrected.cnab240.txt")

        if st.button("📑 Export Validation Report (HTML)"):
            html = "<h3>Validation Report</h3><ul>"
            for err in errors:
                html += f"<li style='color:red'>{err}</li>"
            for fix in suggestions:
                html += f"<li style='color:orange'>{fix}</li>"
            html += "</ul>"
            st.download_button("⬇️ Download Report", html, file_name="validation_report.html", mime="text/html")

        with st.expander("📁 File Header"):
            st.json(parsed.get("file_header", {}))

        for i, batch in enumerate(parsed.get("batches", [])):
            with st.expander(f"📦 Batch #{i + 1}"):
                st.subheader("Batch Header")
                st.json(batch.get("batch_header", {}))

                st.subheader("Segments")
                for idx, segment in enumerate(batch.get("segments", [])):
                    display_segment(segment, idx)

                st.subheader("Batch Trailer")
                st.json(batch.get("batch_trailer", {}))

        with st.expander("📁 File Trailer"):
            st.json(parsed.get("file_trailer", {}))


if __name__ == "__main__":
    main()
