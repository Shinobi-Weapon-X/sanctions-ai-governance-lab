"""Simple demo-only rationale checks - not a regulatory case workflow."""

def review_form_error(reviewer: str, rationale: str) -> str:
    """Empty string when acceptable; clear user-facing error otherwise."""
    if len((rationale or '').strip()) < 20:
        return 'Please provide a meaningful rationale of at least 20 characters.'
    if len((reviewer or '').strip()) < 2:
        return 'Please provide a reviewer pseudonym of at least two characters.'
    return ''
