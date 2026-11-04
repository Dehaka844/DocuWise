from fastapi import UploadFile

from app.chunking.recursive_chunker import RecursiveChunker
from app.ingestion.parser_factory import ParserFactory
from app.models.document import DocumentChunk, ParsedDocument


class DocumentService:

    def __init__(self):

        self.parser_factory = ParserFactory()

        self.chunker = RecursiveChunker()

    async def process_document(
        self,
        file: UploadFile,
    ) -> ParsedDocument:

        parser = self.parser_factory.get_parser(
            file
        )

        return await parser.parse(file)

    async def process_and_chunk_document(
        self,
        file: UploadFile,
        extra_metadata: dict | None = None,
    ) -> list[DocumentChunk]:

        document = await self.process_document(
            file
        )

        chunks = self.chunker.chunk_document(
            document
        )

        if extra_metadata:
            for chunk in chunks:
                chunk.metadata.update(extra_metadata)

        return chunks
