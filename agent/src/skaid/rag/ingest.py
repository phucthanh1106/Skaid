# AI packages
from langchain_core.documents import Document # Document is for retrieval workflows
from langchain_text_splitters import RecursiveCharacterTextSplitter
# Support packages
import json
from pathlib import Path
from dotenv import load_dotenv
import os
# Modules
from src.skaid.rag.client import pc
from src.skaid.config import PINECONE_INDEX_NAME, PINECONE_NAMESPACE, DOCUMENT_PATH

# Some variables
MARKDOWN_SEPARATORS = [
    "\n#{1,6} "
    "` ` ` \n",
    "\n\\*\\*\\*+\n",
    "\n---+\n",
    "\n___+\n",
    "\n\n",
    "\n",
    " ",
    "",
]

# Create a text splitter for chunking the document
text_splitter = RecursiveCharacterTextSplitter(
    chunk_size=1200,
    chunk_overlap=200,
    add_start_index=True,
    strip_whitespace=True,
    separators=MARKDOWN_SEPARATORS,
)

# Run the complete ingestion workflow
def main():
    # Open the file in read mode ('r') with utf-8 encoding
    with open(DOCUMENT_PATH, "r", encoding="utf-8") as f:
        documents = json.load(f)

    # Store all Pinecone records before uploading them
    records = []

    # Convert every JSON document into smaller chunks
    for document_number, document in enumerate(documents):
        metadata = {
            "title": document["title"],
            "url": document["url"]
        }

        langchain_doc = Document(page_content=document["content"], metadata=metadata)
        chunks = text_splitter.split_documents([langchain_doc])

        # Convert every chunk into a Pinecone record
        for chunk_number, chunk in enumerate(chunks):
            record = {
                "_id": f"doc-{document_number}#chunk-{chunk_number}",
                "text": chunk.page_content,
                "title": chunk.metadata["title"],
                "url": chunk.metadata["url"],
                "start_index": chunk.metadata["start_index"]
            }
            records.append(record)

    # Connect to the existing Pinecone index
    index = pc.Index(PINECONE_INDEX_NAME)

    # Embed and store the records in Pinecone
    index.upsert_records(PINECONE_NAMESPACE, records)

# Only ingest when this file is executed directly
if __name__ == "__main__":
    main()