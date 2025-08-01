import streamlit as st
from PIL import Image
import pytesseract
import re
from pdf2image import convert_from_bytes

# Optional: Set Tesseract path (Windows only)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"

def extract_text_from_image(image):
    return pytesseract.image_to_string(image)

def extract_invoice_fields(text):
    fields = {
        "Invoice Number": "",
        "Date": "",
        "Total Amount": ""
    }

    # Updated regex to match your image structure
    invoice_no_match = re.search(r"INVOICE\s*#\s*([A-Z0-9\-]+)", text, re.IGNORECASE)
    date_match = re.search(r"INVOICE\s*DATE\s*[:\-]?\s*(\d{1,2}[/-]\d{1,2}[/-]\d{2,4})", text, re.IGNORECASE)
    total_match = re.search(r"INVOICE\s*TOTAL\s*[₹$]?\s*([\d,]+\.\d{2})", text, re.IGNORECASE)

    if invoice_no_match:
        fields["Invoice Number"] = invoice_no_match.group(1).strip()
    if date_match:
        fields["Date"] = date_match.group(1).strip()
    if total_match:
        fields["Total Amount"] = total_match.group(1).strip()

    return fields


def process_uploaded_file(uploaded_file):
    file_type = uploaded_file.type
    all_text = ""

    if "pdf" in file_type:
        images = convert_from_bytes(uploaded_file.read())
        for i, img in enumerate(images):
            st.image(img, caption=f"Page {i+1}", use_column_width=True)
            text = extract_text_from_image(img)
            all_text += text + "\n"
    else:
        image = Image.open(uploaded_file)
        st.image(image, caption="Uploaded Image", use_column_width=True)
        all_text = extract_text_from_image(image)

    return all_text

# Streamlit UI
st.set_page_config(page_title="Invoice OCR with PDF Support")
st.title("📄 Invoice Extractor (Image + PDF, Offline)")

uploaded_file = st.file_uploader("Upload an invoice (Image or PDF)", type=["png", "jpg", "jpeg", "pdf"])

if uploaded_file:
    if st.button("Extract Invoice Details"):
        with st.spinner("Processing..."):
            extracted_text = process_uploaded_file(uploaded_file)
            fields = extract_invoice_fields(extracted_text)

            st.subheader("🔍 Extracted Invoice Fields:")
            for key, value in fields.items():
                st.write(f"**{key}:** {value if value else 'Not Found'}")

            st.subheader("📃 Raw OCR Text:")
            st.text_area("OCR Output", extracted_text, height=300)
