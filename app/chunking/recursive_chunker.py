from app.models.document import DocumentChunk, ParsedDocument


class RecursiveChunker:

    def __init__(
        self,
        chunk_size: int = 1000,
        chunk_overlap: int = 200,
    ):
        if chunk_size <= 0:
            raise ValueError(
                "chunk_size must be greater than 0"
            )

        if chunk_overlap < 0:
            raise ValueError(
                "chunk_overlap cannot be negative"
            )

        if chunk_overlap >= chunk_size:
            raise ValueError(
                "chunk_overlap must be smaller than chunk_size"
            )

        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap

    def chunk_document(
        self,
        document: ParsedDocument,
    ) -> list[DocumentChunk]:

        chunks = []

        chunk_index = 0

        for page in document.pages:

            page_chunks = self._split_text(
                page.content
            )

            for content in page_chunks:

                chunks.append(
                    DocumentChunk(
                        content=content,
                        metadata={
                            **document.metadata,
                            "page_number": page.page_number,
                            "chunk_index": chunk_index,
                        },
                    )
                )

                chunk_index += 1

        return chunks

    def _split_text(
        self,
        text: str,
    ) -> list[str]:

        if len(text) <= self.chunk_size:
            return [text]

        return self._split_by_separator(
            text,
            separators=[
                "\n\n",
                "\n",
                " ",
                "",
            ],
        )

    def _split_by_separator(
        self,
        text: str,
        separators: list[str],
    ) -> list[str]:

        if not separators:
            return self._split_by_characters(text)

        separator = separators[0]

        if separator == "":
            return self._split_by_characters(text)

        splits = text.split(separator)

        final_splits = []

        small_splits = []

        for split in splits:

            if not split.strip():
                continue

            if len(split) <= self.chunk_size:

                small_splits.append(split)

            else:

                if small_splits:

                    final_splits.extend(
                        self._merge_splits(
                            small_splits,
                            separator,
                        )
                    )

                    small_splits = []

                final_splits.extend(
                    self._split_by_separator(
                        split,
                        separators[1:],
                    )
                )

        if small_splits:

            final_splits.extend(
                self._merge_splits(
                    small_splits,
                    separator,
                )
            )

        return final_splits

    def _merge_splits(
        self,
        splits: list[str],
        separator: str,
    ) -> list[str]:

        chunks = []

        current_parts = []

        current_length = 0

        for split in splits:

            split_length = len(split)

            separator_length = (
                len(separator)
                if current_parts
                else 0
            )

            if (
                current_length
                + separator_length
                + split_length
                <= self.chunk_size
            ):

                current_parts.append(split)

                current_length += (
                    separator_length
                    + split_length
                )

            else:

                if current_parts:

                    chunks.append(
                        separator.join(current_parts)
                    )

                overlap_parts = self._get_overlap_parts(
                    current_parts,
                    separator,
                )

                current_parts = overlap_parts

                current_length = len(
                    separator.join(current_parts)
                )

                separator_length = (
                    len(separator)
                    if current_parts
                    else 0
                )

                if (
                    current_length
                    + separator_length
                    + split_length
                    <= self.chunk_size
                ):

                    current_parts.append(split)

                    current_length = len(
                        separator.join(current_parts)
                    )

                else:

                    current_parts = [split]

                    current_length = split_length

        if current_parts:

            chunks.append(
                separator.join(current_parts)
            )

        return chunks

    def _get_overlap_parts(
        self,
        parts: list[str],
        separator: str,
    ) -> list[str]:

        overlap_parts = []

        overlap_length = 0

        for part in reversed(parts):

            additional_length = len(part)

            if overlap_parts:
                additional_length += len(separator)

            if (
                overlap_length
                + additional_length
                > self.chunk_overlap
            ):
                break

            overlap_parts.insert(
                0,
                part,
            )

            overlap_length += additional_length

        return overlap_parts

    def _split_by_characters(
        self,
        text: str,
    ) -> list[str]:

        chunks = []

        start = 0

        step = (
            self.chunk_size
            - self.chunk_overlap
        )

        while start < len(text):

            end = start + self.chunk_size

            chunks.append(
                text[start:end]
            )

            start += step

        return chunks