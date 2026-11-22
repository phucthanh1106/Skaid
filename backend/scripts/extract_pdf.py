import json
import subprocess
from pathlib import Path
import os
import mysql.connector
from app import config
from app.services.database import get_database

PATH_TO_FOLDER = "/home/thanhtran/Skaid/Presentations"

# Extract text, clean the footer, and preserve PDF page numbers.
def extract_pdf(pdf_path):
    pdf_path = Path(pdf_path)

    # Run Poppler and capture its text output.
    result = subprocess.run(["pdftotext", "-enc", "UTF-8", str(pdf_path), "-"], capture_output=True, text=True, encoding="utf-8", check=True)

    # Split before cleaning so empty pages still count.
    pages = []
    for page_number, page_text in enumerate(result.stdout.split("\f"), start=1):
        # Keep slide content and stop when the known footer begins.
        lines = []
        for line in page_text.splitlines():
            if line.strip() == "(c) 2026 David S. Read":
                break
            lines.append(line)

        # Preserve line breaks in the remaining content.
        text = "\n".join(lines).strip()

        # Keep nonempty pages with their source metadata.
        if text:
            title = text.splitlines()[0].strip()

            # Skip title-only slides.
            if text.strip() == title:
                continue

            pages.append({"filename": pdf_path.name, "page": page_number, "title": title[:500], "text": text})

    return pages


# Store one document and all its extracted pages together.
def save_document(pdf_path, pages, connection):
    # Avoid storing a document with no extracted content.
    if not pages:
        return

    # Open a connection using the backend's existing settings.
    cursor = connection.cursor()

    try:
        # Find an existing document with this filename.
        cursor.execute("SELECT id FROM documents WHERE filename = %s", (pdf_path.name,))
        document = cursor.fetchone()

        # Keep the existing document ID, or create a new document.
        if document:
            document_id = document[0]
            cursor.execute("UPDATE documents SET title = %s WHERE id = %s", (pdf_path.stem, document_id))
        else:
            cursor.execute("INSERT INTO documents (title, filename) VALUES (%s, %s)", (pdf_path.stem, pdf_path.name))
            document_id = cursor.lastrowid

        # Remove only this document's previous pages before inserting replacements.
        cursor.execute("DELETE FROM pages WHERE document_id = %s", (document_id,))

        # Insert the newly extracted pages using the existing loop below.
        for page in pages:
            cursor.execute("INSERT INTO pages (document_id, page_number, title, text) VALUES (%s, %s, %s, %s)", (document_id, page["page"], page["title"], page["text"]))
        # Make the document and its pages permanent together.
        connection.commit()
    except Exception:
        # Undo this document's inserts if any step fails.
        connection.rollback()
        raise
    finally:
        # Close this operation's cursor;
        cursor.close()


# Preview extracted pages without writing an output file.
if __name__ == "__main__":
    folder = Path(PATH_TO_FOLDER)
    database = get_database()
    connection = next(database)

    try:
        # Extract and save each PDF using the actual connection.
        for pdf_path in sorted(folder.glob("*.pdf")):
            pages = extract_pdf(pdf_path)
            save_document(pdf_path, pages, connection)
            print(f"{pdf_path.name}: {len(pages)} pages extracted")
    finally:
        # Run get_database's cleanup to close the connection.
        database.close()