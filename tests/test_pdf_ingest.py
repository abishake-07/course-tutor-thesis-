import re

from core.pdf_ingest import sanitize_extracted_text


def test_sanitize_extracted_text_collapses_whitespace():
    extracted = {
        'body': 'This   is\n\n a   test.\n\n\nNew\tline.',
        'metadata': {'Title': 'Test'},
        'annotations': ['Note:\nPlease ignore.']
    }

    result = sanitize_extracted_text(extracted)

    assert '  ' not in result['body']
    assert '\n' not in result['body']
    assert result['body'].startswith('This is a test.')
    assert isinstance(result['annotations'], list)
