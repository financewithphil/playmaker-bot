"""
CLI script to bulk-upload documents (PDF + DOCX) from a local directory.

Usage:
    python -m app.services.admin_upload ./docs/ --api-url http://localhost:8000 --secret your_admin_secret
"""

import os
import argparse
import requests

SUPPORTED_EXTENSIONS = {".pdf", ".docx"}
MIME_TYPES = {
    ".pdf": "application/pdf",
    ".docx": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
}


def upload_documents(directory: str, api_url: str, secret: str):
    files = [
        f for f in os.listdir(directory)
        if os.path.splitext(f)[1].lower() in SUPPORTED_EXTENSIONS
    ]

    if not files:
        print(f"No supported files found in {directory}")
        return

    print(f"Found {len(files)} documents to upload\n")

    for i, filename in enumerate(sorted(files), 1):
        filepath = os.path.join(directory, filename)
        ext = os.path.splitext(filename)[1].lower()
        mime = MIME_TYPES.get(ext, "application/octet-stream")
        print(f"[{i}/{len(files)}] Uploading: {filename}...", end=" ", flush=True)

        try:
            with open(filepath, "rb") as f:
                response = requests.post(
                    f"{api_url}/api/upload/document",
                    files={"file": (filename, f, mime)},
                    headers={"x-admin-secret": secret},
                    timeout=300,
                )

            if response.ok:
                data = response.json()
                print(f"OK — {data['chunks_created']} chunks")
            else:
                print(f"FAILED — {response.status_code}: {response.text}")
        except Exception as e:
            print(f"ERROR — {e}")

    print("\nDone!")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bulk upload documents to Playmaker Bot")
    parser.add_argument("directory", help="Directory containing PDF/DOCX files")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--secret", required=True, help="Admin secret key")
    args = parser.parse_args()

    upload_documents(args.directory, args.api_url, args.secret)
