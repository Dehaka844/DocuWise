from abc import ABC, abstractmethod

from fastapi import UploadFile

from app.models.document import ParsedDocument


class BaseDocumentParser(ABC):

    @abstractmethod
    async def parse(
        self,
        file: UploadFile,
    ) -> ParsedDocument:
        pass