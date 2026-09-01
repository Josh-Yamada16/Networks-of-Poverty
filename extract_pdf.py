import pdfplumber

pdf_path = r"C:\Users\Josh Yamada\Downloads\Multi-dimensional assignment model and its algorithm-Tian Xie.pdf"

try:
    with pdfplumber.open(pdf_path) as pdf:
        print(f"Total pages: {len(pdf.pages)}\n")
        full_text = ""
        for page_num, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                full_text += text + "\n"
        
        print(full_text)
except Exception as e:
    print(f"Error: {e}")
