from fastapi import UploadFile

from app.ingestion.parsers.base import BaseDocumentParser
from app.models.document import PageContent, ParsedDocument


class MarkdownParser(BaseDocumentParser):

    async def parse(
        self,
        file: UploadFile,
    ) -> ParsedDocument:

        file_content = await file.read()

        content = file_content.decode("utf-8")

        return ParsedDocument(
            pages=[
                PageContent(
                    page_number=1,
                    content=content,
                )
            ],
            metadata={
                "filename": file.filename,
                "source_type": "markdown",
                "page_count": 1,
            },
        )