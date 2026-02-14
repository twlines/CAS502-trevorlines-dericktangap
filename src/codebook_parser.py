import pdfplumber
import re
import json

def parse_codebook(pdf_path):
    """Parse PSED PDF codebook and return dictionary of variable definitions"""
    codebook = {}

    with pdfplumber.open(pdf_path) as pdf:
        # Loop through each page and extract text
        for page in pdf.pages:
            text = page.extract_text()
            if not text:
                continue  # skip blank pages

            # Split page text into lines for parsing
            lines = text.split('\n')

            # track which variable we are currently parsing
            current_var = None

            for line in lines:
                # Detect variable name lines (must contain a digit, e.g. AA4, BG2)
                var_match = re.match(r'^([A-Z]+\d[A-Z0-9_]*)\s+', line)
                if var_match:
                    current_var = var_match.group(1)
                    if current_var not in codebook:
                        codebook[current_var] = {'codes': {}, 'type': 'categorical'}

                # Detect code-label pairs i.e. "1. Yes" or "5. No")
                code_match = re.search(r'(\d+)\.\s+([A-Za-z].+)', line)
                if code_match and current_var:
                    code = int(code_match.group(1))
                    label = code_match.group(2).strip()
                    codebook[current_var]['codes'][code] = label

                # Detect continuous variables (example: "Code number of owners")
                if re.search(r'CODE\s+(NUMBER|AMOUNT|PERCENT)', line):
                    if current_var:
                        codebook[current_var]['type'] = 'continuous'

    return codebook 

if __name__ == "__main__":
    result = parse_codebook("data/37202-0003-Codebook-waves_MULTI.pdf")
    with open("data/codebook.json", "w") as f:
        json.dump(result, f, indent=2)
    print(f"Parsed {len(result)} variables.Saved to data/codebook.json")
