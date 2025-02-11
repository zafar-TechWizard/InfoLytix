import os
import json
import requests
from bs4 import BeautifulSoup
from PyPDF2 import PdfReader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.schema import Document
import logging
# import spacy

# Configure logger
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger(__name__)


# nlp = spacy.load("en_core_web_sm")


def Add_to_Json(documents, filename="./Data/documents.json"):
    """
    Saves the link content to JSON without removing existing content.
    """

    # Step 1: Load existing data if the file exists
    if os.path.exists(filename):
        with open(filename, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                existing_data = []  # Handle empty or corrupted files
    else:
        existing_data = []

    # Step 2: Convert existing data into a dictionary for easy updates
    grouped_docs = {entry["url"] or entry["title"]: entry for entry in existing_data}

    # Step 3: Process new documents
    for doc in documents:
        url = doc.metadata.get("url")
        title = doc.metadata.get("title")

        key = url if url else title  # Use URL if available, otherwise use title

        if key:
            if key not in grouped_docs:
                grouped_docs[key] = {"url": url, "title": title, "documents": []}  # Create new entry

            grouped_docs[key]["documents"].extend(doc.page_content if isinstance(doc.page_content, list) else [doc.page_content])  # Append new content

    # Step 4: Save the updated data back to the JSON file
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(list(grouped_docs.values()), f, indent=4, ensure_ascii=False)

    print(f"Documents successfully updated and saved to {filename}")



def search_documents_for_urls(urls, filename=".\Data\documents.json"):
    """
    Searches for documents matching the given URLs in the saved file.

    :param urls: List of URLs to search for
    :param filename: JSON file where documents are stored
    :return: List of Document objects matching the URLs
    """

    links=[]
    for link in urls:
        if not (link.startswith('http://') or link.startswith('https://')):
            link = f'https://{link}'
            links.append(link)
        else:
            links.append(link)

    try:
        # Load saved documents from JSON file
        with open(filename, "r", encoding="utf-8") as f:
            saved_data = json.load(f)

        result_docs = []

        for entry in saved_data:
            if entry["url"] in links:
                for content in entry["documents"]:
                    result_docs.append(Document(page_content=content, metadata={"title": entry["title"], "url": entry["url"]}))

        return result_docs

    except FileNotFoundError:
        print(f"Error: {filename} not found!")
        return []



# def adaptive_chunking(text):
#     """
#     Splits the text into chunks based on the selected mode.

#     Modes:
#         - 'speed': Large chunks, prioritizing fewer breaks.
#         - 'balanced': Medium chunks, a trade-off between size and detail.
#         - 'insight': Small chunks, focusing on detailed analysis.
#     """
    

    
#     doc = spacy.load("en_core_web_sm")(text)
#     chunks = []
#     current_chunk = []
#     current_length = 0
#     # min_length, max_length = 15000, 20000
#     min_length, max_length = 5000, 10000


#     for sentence in doc.sents:
#         sentence_length = len(sentence.text)

#         # If adding this sentence exceeds the max_length, store the current chunk
#         if current_length + sentence_length > max_length or sentence_length > min_length:
#             if current_chunk:
#                 chunks.append(' '.join(current_chunk))
#             current_chunk = [sentence.text]
#             current_length = sentence_length
#         else:
#             current_chunk.append(sentence.text)
#             current_length += sentence_length

#     if current_chunk:
#         chunks.append(' '.join(current_chunk))
    
#     return chunks




def linkHandler(links):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1500,  # Adjust based on LLM context window
        chunk_overlap=350,  # Ensures continuity between chunks
    )

    docs = []

    data =search_documents_for_urls(links)
    
    if data:
        docs.extend(data)
        print('got from saved')
        return docs



    for link in links:
        if not (link.startswith('http://') or link.startswith('https://')):
            link = f'https://{link}'

        try:
            print('trying from web')
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
                splitted_text = splitter.split_text(parsed_text)
                # splitted_text = adaptive_chunking(parsed_text)

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
                splitted_text = splitter.split_text(plain_text)
                # splitted_text = adaptive_chunking(plain_text)

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

    Add_to_Json(docs)
    return docs

