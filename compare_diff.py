# compare_diff.py
from difflib import HtmlDiff

def generate_diff_table(original_lines, fixed_lines):
    differ = HtmlDiff()
    html_diff = differ.make_table(
        fromlines=original_lines,
        tolines=fixed_lines,
        fromdesc='Original File',
        todesc='Fixed File',
        context=True,
        numlines=3
    )
    return html_diff
