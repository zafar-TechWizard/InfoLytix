import pdfplumber
import pytesseract
from PIL import Image
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document

# Path to Tesseract executable (modify this path for your system)
# pytesseract.pytesseract.tesseract_cmd = r"C:\Program Files\Tesseract-OCR\tesseract.exe"  # Adjust for Windows

def extract_text_with_ocr(page):
    """
    Extracts text from an image-based PDF page using OCR.
    """
    # Convert the page to an image with pdfplumber
    page_image = page.to_image(resolution=300).original  # Convert page to PIL Image
    text = pytesseract.image_to_string(page_image)  # Perform OCR on the image
    return text

def process_pdf(file_path):
    """
    Extracts content from a PDF file (including scanned PDFs) and splits it into smaller chunks.

    Args:
        file_path (str): Path to the PDF file.

    Returns:
        list: A list of LangChain Document objects with the chunked content.
    """
    try:
        # Initialize RecursiveCharacterTextSplitter
        splitter = RecursiveCharacterTextSplitter(chunk_size=500, chunk_overlap=50)
        
        pdf_text = ""
        with pdfplumber.open(file_path) as pdf:
            for page in pdf.pages:
                # Try to extract text normally
                text = page.extract_text()
                if not text:  # If no text, use OCR
                    print(f"OCR applied on page {page.page_number}")
                    text = extract_text_with_ocr(page)
                if text:
                    pdf_text += text + "\n"
        
        if not pdf_text.strip():
            raise ValueError("The PDF file does not contain readable text, even with OCR.")

        # Clean and normalize text
        parsed_text = " ".join(pdf_text.split())

        # Split the text into smaller chunks
        splitted_text = splitter.split_text(parsed_text)

        # Create Document objects for each chunk
        documents = [
            Document(
                page_content=text,
                metadata={"title": "PDF Document", "source": file_path}
            )
            for text in splitted_text
        ]

        return documents

    except Exception as e:
        print(f"An error occurred while processing the PDF: {e}")
        return []


# Example Usage
if __name__ == "__main__":
    # Path to your local PDF file
    pdf_file = "temp.pdf"  # Replace with the path to your PDF file
    documents = process_pdf(pdf_file)

    # Display chunked content
    if documents:
        for idx, doc in enumerate(documents, 1):
            print(f"Chunk {idx}:\n{doc.page_content}\n")
    else:
        print("No content extracted from the PDF.")
