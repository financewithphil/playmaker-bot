"""
CLI script to bulk-upload PDFs from a local directory.

Usage:
    python -m app.services.admin_upload ./pdfs/ --api-url http://localhost:8000 --secret your_admin_secret
"""

import os
import sys
import argparse
import requests


def upload_pdfs(directory: str, api_url: str, secret: str):
    pdf_files = [f for f in os.listdir(directory) if f.lower().endswith(".pdf")]

    if not pdf_files:
        print(f"No PDF files found in {directory}")
        return

    print(f"Found {len(pdf_files)} PDFs to upload\n")

    for i, filename in enumerate(sorted(pdf_files), 1):
        filepath = os.path.join(directory, filename)
        print(f"[{i}/{len(pdf_files)}] Uploading: {filename}...", end=" ", flush=True)

        try:
            with open(filepath, "rb") as f:
                response = requests.post(
                    f"{api_url}/api/upload/pdf",
                    files={"file": (filename, f, "application/pdf")},
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
    parser = argparse.ArgumentParser(description="Bulk upload PDFs to Playmaker Bot")
    parser.add_argument("directory", help="Directory containing PDF files")
    parser.add_argument("--api-url", default="http://localhost:8000", help="API base URL")
    parser.add_argument("--secret", required=True, help="Admin secret key")
    args = parser.parse_args()

    upload_pdfs(args.directory, args.api_url, args.secret)
