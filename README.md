
# 🤖 Go Ask Tasos

A locally running intelligent chatbot that either is modifiable or lets you query the content of your PDFs using Retrieval-Augmented Generation (RAG) and local LLMs via Ollama.

---

## ✨ Features

- 📄 Upload PDFs and automatically extract and index their content
- 🧠 Vector-based indexing stored as `.pkl` files per PDF
- 💬 Chat interface  `llama3`, `gpt-4o-mini` (not connected to RAG) 
- 🧪⚡🧟 modify role and behavior
- 🗂 Choose previously uploaded PDFs without re-indexing
- 🔐 Login-protected user access
- ✅ 100% offline, privacy-friendly, no external API calls

---

## 🚀 Installation

### 1. Clone the repository

```bash
git clone https://github.com/yourusername/go_ask_tasos.git
cd go_ask_tasos


Attention:
🗂 Required Folders
Before running the application, make sure the following folders exist in the project root:

uploads/: this folder stores uploaded PDF files.
vector_store/: this folder stores the vector index .pkl files generated from your PDFs.
If these folders are not present, you can create them manually using the terminal:

mkdir uploads vector_store
💡 Make sure these folders are at the same level as your main Python scripts (e.g., main.py, app.py).


2. Set up the Python environment

python -m venv .venv
source .venv/bin/activate  # macOS/Linux
.venv\Scripts\activate     # Windows

3. Install the dependencies

pip install -r requirements.txt

4. Install and start Ollama and pull models

Install Ollama if not already installed:
https://ollama.com  # for download

ollama serve

!!! Required models (must be pulled before starting the app)
ollama pull nomic-embed-text
ollama pull llama3

5. Run the application

python app.py

🕹️ Usage

Register or log in.
Modify your chatbot, and manage your hole communication.
or
Upload a PDF – its content will be chunked, embedded, and saved as a vector index.
Alternatively: select an existing PDF from the dropdown list.
Enter a question – the bot will respond using the context from the document.
📂 Project Structure

go_ask_tasos/
│
├── app.py                  		# App entry point
├── project/
│   ├── main.py                     # Flask routes
│   ├── auth.py                     # Flask routes to authenticate
│   ├── grogmodel.py                # grog model 
│   ├── chatgptmodel.py.            # chatgpt model
│   ├── models.py                   # db setub
│   ├── ollama_rag.py               # RAG engine using Ollama
│   ├── templates/
│   │   └── pimp-it.html            
│   │   └── modifier.html  			
│   │   └── prompt-area.html  
│   │   └── login.html   
│   │   └── index.html   
│   │   └── base.html   
│   │   └── signup.html      
│   ├── static/                     # CSS 
│   ├── uploads/                    # Uploaded PDFs
│   ├── .env/                       # place your api keys in here
│   └── vector_store/               # Saved vector DBs (.pkl)
├── requirements.txt
└── README.md
⚙️ Configuration

Models in ollama_rag.py are set on default:

EMBEDDING_MODEL = 'hf.co/CompendiumLabs/bge-base-en-v1.5-gguf'
LANGUAGE_MODEL = 'hf.co/bartowski/Llama-3.2-1B-Instruct-GGUF'


✅ To-Do

 Support for .txt, .docx and other formats
 Multilingual chat answers
 Export chat history
 REST API (OpenAPI / Swagger)
 
⚠️ Limitations

Only supports local models available via Ollama
Does not re-index if a PDF is modified after upload
Embeddings and answers depend on Ollama's local runtime


