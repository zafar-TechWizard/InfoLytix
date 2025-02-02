import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import logging
import spacy

# Configure logger
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)



nlp = spacy.load("en_core_web_sm")

def adaptive_chunking(text):
    """
    Splits the text into chunks based on the selected mode.

    Modes:
        - 'speed': Large chunks, prioritizing fewer breaks.
        - 'balanced': Medium chunks, a trade-off between size and detail.
        - 'insight': Small chunks, focusing on detailed analysis.
    """
    

    
    doc = nlp(text)
    chunks = []
    current_chunk = []
    current_length = 0
    min_length, max_length = 1000, 1800

    for sentence in doc.sents:
        sentence_length = len(sentence.text)

        # If adding this sentence exceeds the max_length, store the current chunk
        if current_length + sentence_length > max_length or sentence_length > min_length:
            if current_chunk:
                chunks.append(' '.join(current_chunk))
            current_chunk = [sentence.text]
            current_length = sentence_length
        else:
            current_chunk.append(sentence.text)
            current_length += sentence_length

    if current_chunk:
        chunks.append(' '.join(current_chunk))
    
    return chunks




def linkHandler(links):
    # splitter = RecursiveCharacterTextSplitter(
    #     chunk_size=1000,  # Adjust based on LLM context window
    #     chunk_overlap=300,  # Ensures continuity between chunks
    # )

    docs = []

    for link in links:
        if not (link.startswith('http://') or link.startswith('https://')):
            link = f'https://{link}'

        try:
            response = requests.get(link, stream=True)
            content_type = response.headers.get('Content-Type', '')

            # Check if content is PDF
            if 'application/pdf' in content_type:
                with open('./Data/temp.pdf', 'wb') as f:
                    f.write(response.content)
                pdf_reader = PdfReader('./Data/temp.pdf')
                pdf_text = " ".join([page.extract_text() for page in pdf_reader.pages])
                parsed_text = " ".join(pdf_text.split())  

                # Split text and create documents
                # splitted_text = splitter.split_text(parsed_text)
                splitted_text = adaptive_chunking(parsed_text)

                title = "PDF Document"
                link_docs = [
                    Document(
                        page_content=text,
                        metadata={"title": title, "url": link}
                    )
                    for text in splitted_text
                ]
                docs.extend(link_docs)

            else:
                # Process HTML
                soup = BeautifulSoup(response.text, 'html.parser')
                title = soup.title.string if soup.title else link
                plain_text = soup.get_text(separator=" ", strip=True)

                # Split text and create documents
                # splitted_text = splitter.split_text(plain_text)
                splitted_text = adaptive_chunking(plain_text)

                link_docs = [
                    Document(
                        page_content=text,
                        metadata={"title": title, "url": link}
                    )
                    for text in splitted_text
                ]
                docs.extend(link_docs)

        except Exception as e:
            logger.error(f"Error processing link {link}: {e}")
            docs.append(
                Document(
                    page_content=f"Failed to retrieve content from the link: {str(e)}",
                    metadata={"title": "Failed to retrieve content", "url": link}
                )
            )

    return parsed_text, docs



# if __name__ == "__main__":
#     result = []
#     links = ["https://assets.speakcdn.com/assets/1827/the_complete_book_of_questions_1001.pdf"]
#     documents = get_documents_from_links(links)
#     result.append(documents)
#     print(result)
