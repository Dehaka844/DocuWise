from io import BytesIO

from docx import Document
from docx.table import Table
from fastapi import UploadFile

from app.ingestion.parsers.base import BaseDocumentParser
from app.models.document import PageContent, ParsedDocument


class DOCXParser(BaseDocumentParser):

    def _extract_blocks(self, container) -> list[str]:
        content = []

        for block in container.iter_inner_content():
            if isinstance(block, Table):
                table_content = self._extract_table(block)
                if table_content:
                    content.append(table_content)
                continue

            text = block.text.strip()
            if text:
                content.append(text)

        return content

    def _extract_table(self, table: Table) -> str:
        rows = []

        for row in table.rows:
            cells = []
            seen_cells = set()

            for cell in row.cells:
                cell_element = cell._tc
                if cell_element in seen_cells:
                    continue
                seen_cells.add(cell_element)

                cell_parts = self._extract_blocks(cell)
                cells.append(" ".join(cell_parts).strip())

            if any(cells):
                rows.append(cells)

        if not rows:
            return ""

        headers = rows[0]
        formatted_rows = ["Tabla: " + " | ".join(headers)]

        for row in rows[1:]:
            values = []
            for index, value in enumerate(row):
                label = (
                    headers[index]
                    if index < len(headers) and headers[index]
                    else f"Columna {index + 1}"
                )
                values.append(f"{label}: {value}")

            formatted_rows.append("; ".join(values))

        return "\n".join(formatted_rows)

    async def parse(
        self,
        file: UploadFile,
    ) -> ParsedDocument:

        file_content = await file.read()

        document = Document(
            BytesIO(file_content)
        )

        content = "\n\n".join(
            self._extract_blocks(document)
        )

        return ParsedDocument(
            pages=[
                PageContent(
                    page_number=1,
                    content=content,
                )
            ],
            metadata={
                "filename": file.filename,
                "source_type": "docx",
                "page_count": 1,
            },
        )
