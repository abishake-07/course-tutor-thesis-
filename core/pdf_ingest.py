"""PDF ingestion helpers for document-ingestion attack experiments.

This module provides a light-weight extraction pipeline that returns:
  - body text (concatenated page text)
  - metadata (title, author, keywords, custom fields)
  - annotations (list of annotation texts/comments found)

The goal: emulate an application pipeline that turns PDFs into text inputs
for downstream text-only models (no native vision). Keep extraction simple
and robust; administrators may need to install PyPDF2 for full parsing.
"""
from typing import Dict, List
import logging

try:
    from PyPDF2 import PdfReader
except Exception:
    PdfReader = None

logger = logging.getLogger(__name__)


def extract_text_metadata_annotations(pdf_path: str) -> Dict[str, object]:
    """Extract body text, metadata, and annotations from a PDF file.

    Returns a dict: { 'body': str, 'metadata': dict, 'annotations': [str, ...] }

    If a dependency is missing, returns empty fields but does not raise.
    """
    body = []
    metadata = {}
    annotations = []

    if PdfReader is None:
        logger.warning("PyPDF2 not available; returning empty extraction for %s", pdf_path)
        return {"body": "", "metadata": {}, "annotations": []}

    try:
        reader = PdfReader(pdf_path)

        # metadata
        raw_meta = reader.metadata
        if raw_meta:
            for k, v in raw_meta.items():
                try:
                    metadata[str(k)] = str(v)
                except Exception:
                    metadata[str(k)] = v

        # pages text
        for page in reader.pages:
            try:
                text = page.extract_text() or ""
                body.append(text)
            except Exception:
                # best-effort; continue on errors
                logger.debug("Failed to extract text from a page in %s", pdf_path)

            # basic annotations extraction (if present)
            try:
                annots = page.get("/Annots")
                if annots:
                    for a in annots:
                        try:
                            obj = a.get_object()
                            contents = obj.get('/Contents')
                            if contents:
                                annotations.append(str(contents))
                        except Exception:
                            continue
            except Exception:
                # page may not have annotations or structure differs
                continue

        full_body = "\n".join([p for p in body if p])
        return {"body": full_body, "metadata": metadata, "annotations": annotations}

    except Exception as e:
        logger.exception("Failed to read PDF %s: %s", pdf_path, e)
        return {"body": "", "metadata": {}, "annotations": []}


def strip_metadata(extracted: Dict[str, object]) -> Dict[str, object]:
    """Return a copy of extracted content with metadata removed."""
    return {"body": extracted.get("body", ""), "metadata": {}, "annotations": extracted.get("annotations", [])}


def remove_annotations(extracted: Dict[str, object]) -> Dict[str, object]:
    """Return a copy with annotations removed (useful as a defense)."""
    return {"body": extracted.get("body", ""), "metadata": extracted.get("metadata", {}), "annotations": []}


def sanitize_extracted_text(extracted: Dict[str, object]) -> Dict[str, object]:
    """Apply basic text normalization to extracted body and annotations.

    This is intentionally minimal — integration with `core/defenses.py`
    (text_normalization, delimiter isolation) will improve protections.
    """
    body = extracted.get("body", "")
    annotations = extracted.get("annotations", [])

    # simple normalization: collapse whitespace
    import re
    body_clean = re.sub(r"\s+", " ", body).strip()
    annotations_clean = [re.sub(r"\s+", " ", a).strip() for a in annotations]

    return {"body": body_clean, "metadata": extracted.get("metadata", {}), "annotations": annotations_clean}
