"""
OCR Worker Stub - InfraFabric Series 2 Core

Status: STUB (awaiting implementation)
Spec: /home/setup/navidocs/intelligence/session-2/document-versioning-spec.md
Queue: bull:ocr-processing:* (Redis)

This worker processes OCR jobs from the Bull queue.
- Images: Tesseract.js
- PDFs: pdfjs-dist

Resurrected from forensic swarm search 2025-11-26.
"""

from typing import Optional
import logging

logger = logging.getLogger(__name__)


class OCRProcessor:
    """
    OCR processor for document text extraction.

    Queue Integration:
        - Listens on: bull:ocr-processing:*
        - 9 Redis keys active as of 2025-11-25

    Supported Formats:
        - Images (PNG, JPG, TIFF): via Tesseract
        - PDFs: via pdfjs-dist
    """

    def __init__(self, redis_url: Optional[str] = None):
        self.redis_url = redis_url
        self._initialized = False
        logger.warning("OCRProcessor is a STUB - implementation pending")

    def process_image(self, image_path: str) -> dict:
        """Extract text from image using Tesseract."""
        raise NotImplementedError("OCRProcessor.process_image() not yet implemented")

    def process_pdf(self, pdf_path: str) -> dict:
        """Extract text from PDF using pdfjs-dist."""
        raise NotImplementedError("OCRProcessor.process_pdf() not yet implemented")

    def start_worker(self):
        """Start listening to Bull queue for OCR jobs."""
        raise NotImplementedError("OCRProcessor.start_worker() not yet implemented")


# Placeholder for Bull queue job handler
def handle_ocr_job(job_data: dict) -> dict:
    """
    Bull queue job handler.

    Expected job_data:
        {
            "type": "image" | "pdf",
            "path": "/path/to/document",
            "options": {...}
        }
    """
    raise NotImplementedError("OCR job handler not yet implemented")
