from pathlib import Path

from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[2]

DATA_DIR = BASE_DIR / "data" / "raw"
VECTORSTORE_DIR = BASE_DIR / "vectorstore"


# ============================================================
# CONFIGURATION
# ============================================================

CHUNK_SIZE = 800
CHUNK_OVERLAP = 150

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"


# ============================================================
# LOAD PDF DOCUMENTS
# ============================================================

def load_documents():
    documents = []

    pdf_files = sorted(DATA_DIR.glob("*.pdf"))

    if not pdf_files:
        raise FileNotFoundError(
            f"No PDF files found in {DATA_DIR}"
        )

    print(f"\nFound {len(pdf_files)} PDF files.\n")

    for pdf_path in pdf_files:

        print(f"Loading: {pdf_path.name}")

        loader = PyPDFLoader(str(pdf_path))
        pdf_documents = loader.load()

        for document in pdf_documents:

            document.metadata["source"] = pdf_path.name

            # PyPDFLoader uses 0-based page numbering.
            # Convert to human-readable 1-based numbering.
            if "page" in document.metadata:
                document.metadata["page"] = (
                    document.metadata["page"] + 1
                )

        documents.extend(pdf_documents)

        print(
            f"  → {len(pdf_documents)} pages loaded"
        )

    print(
        f"\nTotal pages loaded: {len(documents)}"
    )

    return documents


# ============================================================
# SPLIT DOCUMENTS INTO CHUNKS
# ============================================================

def split_documents(documents):

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        separators=[
            "\n\n",
            "\n",
            ". ",
            " ",
            "",
        ],
    )

    chunks = splitter.split_documents(documents)

    # Add unique chunk IDs
    for index, chunk in enumerate(chunks):

        chunk.metadata["chunk_id"] = index

    print(
        f"Created {len(chunks)} chunks"
    )

    return chunks


# ============================================================
# CREATE EMBEDDINGS + FAISS
# ============================================================

def create_vectorstore(chunks):

    print("\nLoading embedding model...")
    print(f"Model: {EMBEDDING_MODEL}")

    embeddings = HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL,
        model_kwargs={
            "device": "cpu"
        },
        encode_kwargs={
            "normalize_embeddings": True
        },
    )

    print("\nCreating FAISS vector database...")

    vectorstore = FAISS.from_documents(
        documents=chunks,
        embedding=embeddings,
    )

    VECTORSTORE_DIR.mkdir(
        parents=True,
        exist_ok=True,
    )

    vectorstore.save_local(
        str(VECTORSTORE_DIR)
    )

    print(
        f"\nVector database saved to:"
        f"\n{VECTORSTORE_DIR}"
    )

    return vectorstore


# ============================================================
# MAIN
# ============================================================

def main():

    print("=" * 60)
    print("FinAI - RAG Knowledge Base Ingestion")
    print("=" * 60)

    documents = load_documents()

    chunks = split_documents(
        documents
    )

    create_vectorstore(
        chunks
    )

    print("\n" + "=" * 60)
    print("INGESTION COMPLETE")
    print("=" * 60)

    print(
        f"\nDocuments: {len(documents)} pages"
    )

    print(
        f"Chunks: {len(chunks)}"
    )

    print(
        f"Vector store: {VECTORSTORE_DIR}"
    )


if __name__ == "__main__":
    main()