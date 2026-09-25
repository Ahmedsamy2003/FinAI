from pathlib import Path
from typing import List, Dict, Any

from langchain_community.vectorstores import FAISS
from langchain_huggingface import HuggingFaceEmbeddings


# ============================================================
# PATHS
# ============================================================

BASE_DIR = Path(__file__).resolve().parents[3]

VECTORSTORE_DIR = BASE_DIR / "vectorstore"


# ============================================================
# CONFIGURATION
# ============================================================

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

DEFAULT_TOP_K = 4


# ============================================================
# CACHED RESOURCES
# ============================================================

_embeddings = None
_vectorstore = None


# ============================================================
# EMBEDDINGS
# ============================================================

def load_embeddings():
    """
    Load the embedding model once and reuse it.

    The model is cached in memory so we don't reload
    MiniLM for every user request.
    """

    global _embeddings

    if _embeddings is None:

        print("Loading embedding model...")

        _embeddings = HuggingFaceEmbeddings(
            model_name=EMBEDDING_MODEL,
            model_kwargs={
                "device": "cpu"
            },
            encode_kwargs={
                "normalize_embeddings": True
            },
        )

        print("Embedding model loaded.")

    return _embeddings


# ============================================================
# VECTOR STORE
# ============================================================

def load_vectorstore():
    """
    Load the FAISS vector database once and reuse it.
    """

    global _vectorstore

    if _vectorstore is not None:
        return _vectorstore

    if not VECTORSTORE_DIR.exists():
        raise FileNotFoundError(
            f"Vector store not found at: {VECTORSTORE_DIR}"
        )

    print("Loading FAISS vector database...")

    embeddings = load_embeddings()

    _vectorstore = FAISS.load_local(
        folder_path=str(VECTORSTORE_DIR),
        embeddings=embeddings,
        allow_dangerous_deserialization=True,
    )

    print("FAISS vector database loaded.")

    return _vectorstore


# ============================================================
# RETRIEVAL
# ============================================================

def retrieve_documents(
    query: str,
    top_k: int = DEFAULT_TOP_K,
) -> List[Dict[str, Any]]:
    """
    Retrieve the most relevant financial knowledge chunks.

    Returns:
        A list containing:
        - content
        - source
        - page
        - chunk_id
    """

    if not query or not query.strip():
        raise ValueError(
            "Query cannot be empty."
        )

    vectorstore = load_vectorstore()

    documents = vectorstore.similarity_search(
        query,
        k=top_k,
    )

    results = []

    for rank, document in enumerate(
        documents,
        start=1,
    ):

        results.append(
            {
                "rank": rank,
                "content": document.page_content,
                "source": document.metadata.get(
                    "source",
                    "Unknown",
                ),
                "page": document.metadata.get(
                    "page",
                    "Unknown",
                ),
                "chunk_id": document.metadata.get(
                    "chunk_id",
                    "Unknown",
                ),
            }
        )

    return results