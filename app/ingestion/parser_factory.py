from pathlib import Path

from fastapi import HTTPException, UploadFile

from app.ingestion.parsers.base import BaseDocumentParser
from app.ingestion.parsers.docx_parser import DOCXParser
from app.ingestion.parsers.markdown_parser import MarkdownParser
from app.ingestion.parsers.pdf_parser import PDFParser


class ParserFactory:

    def __init__(self):
        self.parsers: dict[str, BaseDocumentParser] = {
            ".pdf": PDFParser(),
            ".docx": DOCXParser(),
            ".md": MarkdownParser(),
        }


    def get_parser(
        self,
        file: UploadFile,
    ) -> BaseDocumentParser:

        if not file.filename:
            raise HTTPException(
                status_code=400,
                detail="Filename is required",
            )

        extension = Path(
            file.filename
        ).suffix.lower()

        parser = self.parsers.get(
            extension
        )

        if parser is None:
            raise HTTPException(
                status_code=415,
                detail="Unsupported file type",
            )

        return parser