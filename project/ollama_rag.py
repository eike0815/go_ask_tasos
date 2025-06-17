import ollama
import fitz  # PyMuPDF
import os
import pickle


"""# Configuration
EMBEDDING_MODEL = 'hf.co/CompendiumLabs/bge-base-en-v1.5-gguf'
LANGUAGE_MODEL = 'hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF'"""
# Configuration (recommended defaults)
EMBEDDING_MODEL = 'nomic-embed-text'
LANGUAGE_MODEL = 'llama3'


# In-memory vector store
VECTOR_DB = []

# Folder for saved vector files
VECTOR_INDEX_FOLDER = os.path.join(os.path.dirname(__file__), 'vector_store')
os.makedirs(VECTOR_INDEX_FOLDER, exist_ok=True)


def add_chunk_to_db(chunk: str):
    """Convert chunk to embedding and add it to VECTOR_DB."""
    embedding_resp = ollama.embed(model=EMBEDDING_MODEL, input=chunk)
    embedding = embedding_resp['embeddings'][0]
    VECTOR_DB.append((chunk, embedding))


def extract_text_chunks_from_pdf(pdf_path: str, chunk_size: int = 500) -> list:
    """Extract text from PDF and split into clean chunks."""
    doc = fitz.open(pdf_path)
    full_text = "".join(page.get_text() for page in doc)
    return [
        full_text[i:i + chunk_size].strip()
        for i in range(0, len(full_text), chunk_size)
        if full_text[i:i + chunk_size].strip()
    ]


def save_vector_db(pdf_filename: str):
    """Save VECTOR_DB to disk as a .pkl file based on PDF name."""
    filename = os.path.splitext(os.path.basename(pdf_filename))[0] + '.pkl'
    filepath = os.path.join(VECTOR_INDEX_FOLDER, filename)
    with open(filepath, 'wb') as f:
        pickle.dump(VECTOR_DB, f)
    print(f'✅ Saved vector index to {filepath}')


def load_vector_db(pdf_filename: str):
    """Load .pkl vector index from disk based on PDF filename."""
    global VECTOR_DB
    filename = os.path.splitext(os.path.basename(pdf_filename))[0] + '.pkl'
    filepath = os.path.join(VECTOR_INDEX_FOLDER, filename)
    if os.path.exists(filepath):
        with open(filepath, 'rb') as f:
            VECTOR_DB = pickle.load(f)
        print(f'📂 Loaded vector index from {filepath}')
    else:
        print(f'⚠️ No vector index found for {filepath}')
        VECTOR_DB = []


def build_index_from_pdf(pdf_path: str, chunk_size: int = 500):
    """Build new index from PDF and save it."""
    VECTOR_DB.clear()
    chunks = extract_text_chunks_from_pdf(pdf_path, chunk_size)
    for i, chunk in enumerate(chunks):
        add_chunk_to_db(chunk)
        print(f'🧩 Added chunk {i + 1}/{len(chunks)}')
    save_vector_db(pdf_path)


def cosine_similarity(a: list, b: list) -> float:
    """Calculate cosine similarity between two vectors."""
    dot_product = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    return dot_product / (norm_a * norm_b) if norm_a and norm_b else 0.0


def retrieve(query: str, top_n: int = 3) -> list:
    """Find most relevant chunks based on similarity to query."""
    if not VECTOR_DB:
        return []

    query_embedding = ollama.embed(model=EMBEDDING_MODEL, input=query)['embeddings'][0]
    similarities = [(chunk, cosine_similarity(query_embedding, emb)) for chunk, emb in VECTOR_DB]
    similarities.sort(key=lambda x: x[1], reverse=True)
    return similarities[:top_n]


def generate_answer(query: str) -> str:
    """Generate answer using retrieved context and Ollama LLM."""
    retrieved = retrieve(query)
    if not retrieved:
        return "⚠️ No context available. Please upload or select a PDF first."

    context = ''.join([f' - {chunk}\n' for chunk, _ in retrieved])
    system_prompt = f"""You are a helpful assistant.
Use only the following context to answer the question. Do not invent information:
{context}"""

    response = ollama.chat(
        model=LANGUAGE_MODEL,
        messages=[
            {'role': 'system', 'content': system_prompt},
            {'role': 'user', 'content': query},
        ],
        stream=False
    )

    print(response)  # DEBUG

    if 'choices' in response:
        return response['choices'][0]['message']['content']
    elif 'message' in response:
        return response['message'].get('content', '')
    elif 'text' in response:
        return response['text']
    else:
        return "❌ No valid response from model."
