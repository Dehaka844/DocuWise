from app.chunking.recursive_chunker import RecursiveChunker


def test_small_text():

    chunker = RecursiveChunker(
        chunk_size=100,
        chunk_overlap=20,
    )

    text = "Hola mundo"

    chunks = chunker._split_text(text)

    assert chunks == [
        "Hola mundo"
    ]


def test_chunk_size():

    chunker = RecursiveChunker(
        chunk_size=20,
        chunk_overlap=5,
    )

    text = (
        "Primera frase. "
        "Segunda frase. "
        "Tercera frase. "
        "Cuarta frase."
    )

    chunks = chunker._split_text(text)

    assert len(chunks) > 1

    for chunk in chunks:
        assert len(chunk) <= 20


def test_character_overlap():

    chunker = RecursiveChunker(
        chunk_size=10,
        chunk_overlap=3,
    )

    text = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"

    chunks = chunker._split_by_characters(
        text
    )

    assert chunks == [
        "ABCDEFGHIJ",
        "HIJKLMNOPQ",
        "OPQRSTUVWX",
        "VWXYZ",
    ]