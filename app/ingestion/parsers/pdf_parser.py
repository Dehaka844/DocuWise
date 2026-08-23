import pymupdf

from fastapi import UploadFile

from app.ingestion.parsers.base import BaseDocumentParser
from app.models.document import PageContent, ParsedDocument


class PDFParser(BaseDocumentParser):

    async def parse(
        self,
        file: UploadFile,
    ) -> ParsedDocument:

        file_content = await file.read()

        pdf_document = pymupdf.open(
            stream=file_content,
            filetype="pdf",
        )

        pages = []

        for page_number, page in enumerate(
            pdf_document,
            start=1,
        ):
            page_text = page.get_text()

            pages.append(
                PageContent(
                    page_number=page_number,
                    content=page_text,
                )
            )

        return ParsedDocument(
            pages=pages,
            metadata={
                "filename": file.filename,
                "source_type": "pdf",
                "page_count": len(pdf_document),
            },
        )