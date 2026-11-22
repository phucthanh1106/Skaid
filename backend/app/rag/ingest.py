import os
import subprocess
from pathlib import Path

import requests
from app.services.database import get_database

# Configure the PDF folder, embedding model, and Qdrant connection.
PATH_TO_FOLDER = Path("/home/thanhtran/Skaid/Presentations")
OLLAMA_URL = os.environ["OLLAMA_URL"]
MODEL = "qwen3-embedding:0.6b"
QDRANT_URL = os.environ["QDRANT_URL"].rstrip("/")
QDRANT_API_KEY = os.environ["QDRANT_API_KEY"]
COLLECTION = "qwen3_embedding_06b_pages"


# Extract slide text while preserving the original PDF page numbers.
def extract_pdf(pdf_path):
    result = subprocess.run(["pdftotext", "-enc", "UTF-8", str(pdf_path), "-"], capture_output=True, text=True, encoding="utf-8", check=True)
    pages = []

    # Split into pages before cleaning their content.
    for page_number, page_text in enumerate(result.stdout.split("\f"), start=1):
        lines = []

        # Remove the copyright footer and everything below it.
        for line in page_text.splitlines():
            if line.strip() == "(c) 2026 David S. Read":
                break
            lines.append(line)

        # Skip empty pages.
        text = "\n".join(lines).strip()
        if not text:
            continue

        # Use the first line as the title and skip title-only pages.
        title = text.splitlines()[0].strip()
        if text == title:
            continue

        pages.append({
            "page": page_number,
            "title": title[:500],
            "text": text
        })

    return pages


# Save a new PDF or reuse its existing MySQL pages and IDs.
def save_document(pdf_path, pages):
    database = get_database()
    connection = next(database)

    try:
        cursor = connection.cursor(dictionary=True)

        try:
            # Check whether this filename is already stored.
            cursor.execute("SELECT id FROM documents WHERE filename = %s", (pdf_path.name,))
            document = cursor.fetchone()

            # Return existing pages without replacing or modifying them.
            if document:
                document_id = document["id"]
                cursor.execute("SELECT id AS page_id, page_number AS page, title, text FROM pages WHERE document_id = %s ORDER BY page_number", (document_id,))
                stored_pages = cursor.fetchall()
                return document_id, stored_pages

            # Create a record for a new PDF.
            cursor.execute("INSERT INTO documents (title, filename) VALUES (%s, %s)", (pdf_path.stem, pdf_path.name))
            document_id = cursor.lastrowid

            # Save its pages and remember their generated IDs.
            for page in pages:
                cursor.execute("INSERT INTO pages (document_id, page_number, title, text) VALUES (%s, %s, %s, %s)", (document_id, page["page"], page["title"], page["text"]))
                page["page_id"] = cursor.lastrowid

            # Commit the new document and all its pages together.
            connection.commit()
            return document_id, pages

        except Exception:
            # Undo incomplete inserts if saving fails.
            connection.rollback()
            raise

        finally:
            cursor.close()

    finally:
        # Release the connection before embedding starts.
        database.close()


# Send text to Ollama on Pi 3 and return its embedding vector.
def embed_text(text):
    payload = {
        "model": MODEL,
        "input": text,
        "truncate": False,
        "keep_alive": "10m"
    }

    response = requests.post(f"{OLLAMA_URL}/api/embed", json=payload, timeout=300)
    response.raise_for_status()

    data = response.json()
    return data["embeddings"][0]


# Embed pages and insert or update their Qdrant points.
def index_pages(pdf_path, document_id, pages):
    headers = {"api-key": QDRANT_API_KEY}
    collection_url = f"{QDRANT_URL}/collections/{COLLECTION}"

    # Check whether the collection exists.
    response = requests.get(f"{collection_url}/exists", headers=headers, timeout=30)
    response.raise_for_status()
    collection_exists = response.json()["result"]["exists"]

    for page in pages:
        print(f"Embedding PDF page {page['page']}", flush=True)
        vector = embed_text(page["text"])

        # Create the collection using the model's actual vector dimensions.
        if not collection_exists:
            settings = {
                "vectors": {
                    "size": len(vector),
                    "distance": "Cosine"
                }
            }

            response = requests.put(collection_url, headers=headers, json=settings, timeout=60)
            response.raise_for_status()
            collection_exists = True

        # Store source information for retrieval and citations.
        metadata = {
            "page_id": page["page_id"],
            "document_id": document_id,
            "filename": pdf_path.name,
            "document_title": pdf_path.stem,
            "page_title": page["title"],
            "page_number": page["page"],
            "text": page["text"],
            "embedding_model": MODEL
        }

        # Reusing the page ID makes this an upsert.
        point = {
            "id": page["page_id"],
            "vector": vector,
            "payload": metadata
        }

        # Wait until Qdrant stores the point before continuing.
        response = requests.put(f"{collection_url}/points?wait=true", headers=headers, json={"points": [point]}, timeout=60)
        response.raise_for_status()

        print(f"Stored page ID {page['page_id']}", flush=True)


# Process PDFs through extraction, MySQL storage, and vector indexing.
def main():
    for pdf_path in sorted(PATH_TO_FOLDER.glob("*.pdf")):
        print(f"Processing {pdf_path.name}", flush=True)
        pages = extract_pdf(pdf_path)

        # Skip PDFs without usable extracted text.
        if not pages:
            print("Skipped: no usable text.", flush=True)
            continue

        # Existing documents return their stored pages and original IDs.
        document_id, pages = save_document(pdf_path, pages)

        if not pages:
            print("Skipped: no stored pages.", flush=True)
            continue

        # Report success only after every page is indexed.
        index_pages(pdf_path, document_id, pages)
        print(f"Ready: {pdf_path.name}, {len(pages)} pages indexed.", flush=True)


# Start ingestion when executed as a module.
if __name__ == "__main__":
    main()