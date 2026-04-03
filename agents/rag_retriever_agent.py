"""
RAG Retriever Agent - Retrieves relevant paper chunks from ChromaDB
Single Responsibility: Vector store retrieval ONLY
"""

import os
from config import RAG_TOP_K, RAG_CHUNK_SIZE, EMBEDDING_MODEL


class RAGRetrieverAgent:
    """
    Retrieves relevant chunks from a ChromaDB vector store.
    Replaces SearchAgent in the RAG evaluation path.
    """

    required_inputs = ['query']

    def __init__(self, collection_name="research_papers", top_k=RAG_TOP_K):
        self.collection_name = collection_name
        self.top_k = top_k
        self._client = None
        self._collection = None

    def _get_collection(self):
        """Lazy initialization of ChromaDB client"""
        if self._client is None:
            try:
                import chromadb
                from chromadb.config import Settings
                self._client = chromadb.PersistentClient(
                    path="data/chromadb",
                    settings=Settings(anonymized_telemetry=False)
                )
                self._collection = self._client.get_or_create_collection(
                    name=self.collection_name,
                    metadata={"hnsw:space": "cosine"}
                )
            except ImportError:
                raise ImportError(
                    "ChromaDB not installed. Run: pip install chromadb"
                )
        return self._collection

    def ingest_pdf(self, filepath: str) -> dict:
        """
        Ingest a PDF into the vector store.
        Chunks text, embeds, and stores in ChromaDB.
        """
        try:
            from utils.pdf_parser import extract_text_from_pdf
            from openai import OpenAI
            import hashlib

            pdf_data = extract_text_from_pdf(filepath)
            if not pdf_data['success']:
                return {'success': False, 'error': pdf_data['error']}

            text = pdf_data.get('text', '')
            words = text.split()
            chunks = [
                ' '.join(words[i:i + RAG_CHUNK_SIZE])
                for i in range(0, len(words), RAG_CHUNK_SIZE)
            ]

            client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))
            collection = self._get_collection()

            doc_id = hashlib.md5(filepath.encode()).hexdigest()[:8]
            ids, docs, metas = [], [], []

            for i, chunk in enumerate(chunks):
                if chunk.strip():
                    ids.append(f"{doc_id}_chunk_{i}")
                    docs.append(chunk)
                    metas.append({
                        "source": os.path.basename(filepath),
                        "chunk_index": i,
                        "total_chunks": len(chunks)
                    })

            if ids:
                collection.upsert(documents=docs, ids=ids, metadatas=metas)

            return {
                'success': True,
                'chunks_ingested': len(ids),
                'source': filepath
            }

        except Exception as e:
            return {'success': False, 'error': str(e)}

    def run(self, input_data: dict) -> dict:
        """Retrieve top-K relevant chunks for a query"""
        query = input_data.get('query', '')
        if not query:
            return {'success': False, 'error': 'No query provided', 'papers': []}

        try:
            collection = self._get_collection()
            count = collection.count()

            if count == 0:
                return {
                    'success': False,
                    'error': 'Vector store is empty. Ingest PDFs first.',
                    'papers': []
                }

            results = collection.query(
                query_texts=[query],
                n_results=min(self.top_k, count)
            )

            papers = []
            docs = results.get('documents', [[]])[0]
            metas = results.get('metadatas', [[]])[0]
            distances = results.get('distances', [[]])[0]

            for doc, meta, dist in zip(docs, metas, distances):
                papers.append({
                    'title': meta.get('source', 'Unknown'),
                    'abstract': doc,
                    'year': 'Unknown',
                    'authors': [],
                    'source': 'ChromaDB',
                    'relevance_score': round(1 - dist, 4),
                    'chunk_index': meta.get('chunk_index', 0)
                })

            return {
                'success': True,
                'papers': papers,
                'count': len(papers),
                'retrieval_source': 'chromadb'
            }

        except Exception as e:
            return {'success': False, 'error': str(e), 'papers': []}


def create_rag_retriever_agent(collection_name="research_papers"):
    return RAGRetrieverAgent(collection_name=collection_name)
