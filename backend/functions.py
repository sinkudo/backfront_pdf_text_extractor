from typing import List

from pdfminer.layout import LTPage, LTTextLine, LTTextBox


def extract_text_per_page(pages: List[LTPage]) -> List[str]:
    return [extract_text_from_ltpage(page) for page in pages]


def extract_text_from_ltpage(page: LTPage) -> str:
    text_parts = []
    for element in page:
        if isinstance(element, (LTTextBox, LTTextLine)):
            text_parts.append(element.get_text())
    return "".join(text_parts).strip()
