import streamlit as st
import pdfplumber
import pytesseract
from PIL import Image
import fitz  # PyMuPDF
import re

def extract_text_from_pdf(pdf_path):
    all_text = ""

    # Open the PDF using pdfplumber
    with pdfplumber.open(pdf_path) as pdf:
        for i, page in enumerate(pdf.pages):
            # Extract text using pdfplumber (native text PDFs)
            page_text = page.extract_text()
            if page_text:
                all_text += f"\n--- Page {i + 1} ---\n" + page_text
            else:
                # If no text found, try OCR on scanned images
                st.warning(f"No text found on page {i + 1}. Trying OCR...")
                image_text = extract_text_from_pdf_image(pdf_path, i)
                all_text += f"\n--- OCR from Page {i + 1} ---\n" + image_text

    return all_text if all_text.strip() else "No text extracted from the PDF."

def extract_text_from_pdf_image(pdf_path, page_num):
    try:
        # Open the PDF page as an image using PyMuPDF
        doc = fitz.open(pdf_path)
        page = doc.load_page(page_num)
        pix = page.get_pixmap()  # Render page as an image
        img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)

        # Run OCR on the image using pytesseract
        text = pytesseract.image_to_string(img)
        return text if text.strip() else "No readable text found via OCR."
    except Exception as e:
        return f"Error during OCR extraction: {e}"

def split_pathology_report(text):
    # Define common sections in pathology reports
    sections = {
        "Patient Information": r"(Patient Information|Patient Name|MRN|ID|DOB)",
        "Clinical History": r"(Clinical History|Medical History|Reason for Visit)",
        "Diagnosis": r"(Diagnosis|Impression|Final Diagnosis)",
        "Specimen Details": r"(Specimen|Sample|Tissue Type|Collected)",
        "Findings": r"(Findings|Microscopic Description|Macroscopic Description)",
        "Conclusion": r"(Conclusion|Summary|Comments)",
    }

    # Initialize a dictionary to store each section's text
    report_parts = {key: "" for key in sections}

    # Use regular expressions to split the text based on section headers
    current_section = None
    for line in text.splitlines():
        for section, pattern in sections.items():
            if re.search(pattern, line, re.IGNORECASE):
                current_section = section
                break

        if current_section:
            report_parts[current_section] += line + "\n"

    return report_parts

# Streamlit App Interface
st.title("Pathology Report Extractor")

uploaded_file = st.file_uploader("Upload a Pathology Report (PDF)", type="pdf")

if uploaded_file is not None:
    with st.spinner("Extracting text from the PDF..."):
        extracted_text = extract_text_from_pdf(uploaded_file)

        st.subheader("Extracted Text")
        st.text_area("Full Report Text", extracted_text, height=300)

        # Split the report into sections
        split_report = split_pathology_report(extracted_text)

        st.subheader("Report Sections")
        for section, content in split_report.items():
            st.markdown(f"### {section}")
            st.text_area(f"{section}", content, height=150)
# import streamlit as st
# import pdfplumber
# import pytesseract
# from PIL import Image
# import fitz  # PyMuPDF
# import re
# import io

# def extract_text_from_pdf(uploaded_file):
#     """Extract text from the uploaded PDF."""
#     all_text = ""
#     with pdfplumber.open(uploaded_file) as pdf:
#         for i, page in enumerate(pdf.pages):
#             page_text = page.extract_text()
#             if page_text:
#                 all_text += f"\n--- Page {i + 1} ---\n" + page_text
#             else:
#                 st.warning(f"No text found on page {i + 1}. Trying OCR...")
#                 image_text = extract_text_from_pdf_image(uploaded_file, i)
#                 all_text += f"\n--- OCR from Page {i + 1} ---\n" + image_text

#     return all_text if all_text.strip() else "No text extracted from the PDF."

# def extract_text_from_pdf_image(uploaded_file, page_num):
#     """Run OCR on a specific page of the uploaded PDF."""
#     try:
#         doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
#         page = doc.load_page(page_num)
#         pix = page.get_pixmap()
#         img = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
#         text = pytesseract.image_to_string(img)
#         return text if text.strip() else "No readable text found via OCR."
#     except Exception as e:
#         return f"Error during OCR extraction: {e}"

# def extract_images_from_pdf(uploaded_file):
#     """Extract all images from the uploaded PDF."""
#     doc = fitz.open(stream=uploaded_file.read(), filetype="pdf")
#     images = []

#     for page_num in range(len(doc)):
#         page = doc.load_page(page_num)
#         for img_index, img in enumerate(page.get_images(full=True)):
#             xref = img[0]
#             base_image = doc.extract_image(xref)
#             image_bytes = base_image["image"]
#             image = Image.open(io.BytesIO(image_bytes))
#             images.append((page_num + 1, img_index + 1, image))

#     return images

# # Streamlit App Interface
# st.title("Pathology Report Extractor with Image Support")

# uploaded_file = st.file_uploader("Upload a Pathology Report (PDF)", type="pdf")

# if uploaded_file is not None:
#     with st.spinner("Extracting text and images..."):
#         # Extract and display text
#         extracted_text = extract_text_from_pdf(uploaded_file)

#         st.subheader("Extracted Text")
#         st.text_area("Full Report Text", extracted_text, height=300)

#         # Extract and display images
#         uploaded_file.seek(0)  # Reset the file pointer after reading text
#         images = extract_images_from_pdf(uploaded_file)

#         if images:
#             st.subheader("Extracted Images")
#             for page_num, img_index, image in images:
#                 st.markdown(f"**Page {page_num} - Image {img_index}**")
#                 st.image(image, caption=f"Page {page_num} - Image {img_index}", use_column_width=True)

#                 # Provide a download button for the image
#                 image_buffer = io.BytesIO()
#                 image.save(image_buffer, format="PNG")
#                 st.download_button(
#                     label=f"Download Image {img_index} from Page {page_num}",
#                     data=image_buffer.getvalue(),
#                     file_name=f"page_{page_num}_image_{img_index}.png",
#                     mime="image/png"
#                 )
#         else:
#             st.info("No images found in the PDF.")
