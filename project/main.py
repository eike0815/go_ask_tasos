from flask import Blueprint, render_template, request, session, jsonify, redirect, url_for, flash
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from project import grogmodel, chatgptmodel, rag, ollama_rag
from . import db
from .models import Chat, User, SystemPrompt
import os

basedir = os.path.abspath(os.path.dirname(__file__))

main = Blueprint('main', __name__)

# Folder to store uploaded PDFs - make sure this folder exists in your project
UPLOAD_FOLDER = os.path.join(basedir, 'uploads')
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """Check if the file has an allowed extension."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@main.route('/')
def index():
    """Render homepage."""
    return render_template('index.html')

@main.route('/Prompt-area', methods=["POST", "GET"])
@login_required
def prompt_area():
    """
    Main chat interface:
    - Handles user prompts
    - Supports model selection (grog, chatgpt)
    - Displays chat history and system prompts for the user
    - Allows deletion of individual chat messages
    """
    user_id = current_user.id
    selected_model = request.args.get("modell", "grog")
    new_prompt = request.args.get("prompt")
    system_prompt_id = request.args.get("system_prompt_id")

    # Handle deletion
    delete_id = request.form.get("delete_chat_id")
    if delete_id:
        chat_to_delete = Chat.query.filter_by(id=delete_id, user_id=user_id).first()
        if chat_to_delete:
            db.session.delete(chat_to_delete)
            db.session.commit()

    # Load system prompts + selected
    system_prompts = SystemPrompt.query.all()
    selected_system_prompt = SystemPrompt.query.get(system_prompt_id) if system_prompt_id else None

    system_msg = None
    temperature = 0.7
    max_tokens = 150
    if selected_system_prompt:
        system_msg = {
            "role": selected_system_prompt.role,
            "content": selected_system_prompt.content
        }
        temperature = selected_system_prompt.temperature
        max_tokens = selected_system_prompt.max_tokens

    if new_prompt:
        context_chats = Chat.query.filter_by(user_id=user_id).order_by(Chat.id.desc()).limit(30).all()
        context_chats.reverse()
        context = "".join([f"User: {chat.question}\nAI: {chat.answer}\n" for chat in context_chats])

        use_rag = request.args.get("use_rag") == "on"
        if use_rag:
            retrieved_docs = rag.retrieve_relevant_docs(new_prompt)
            rag_context = "\n".join(retrieved_docs)
            combined_prompt = rag_context + "\n\n" + context + f"User: {new_prompt}"
        else:
            combined_prompt = context + f"User: {new_prompt}"

        if selected_model == "grog":
            answer = grogmodel.give_answer(combined_prompt, system_prompt_override=system_msg, temperature=temperature, max_tokens=max_tokens)
        elif selected_model == "chatgpt":
            answer = chatgptmodel.chat_answers_question(combined_prompt, system_prompt_override=system_msg, temperature=temperature, max_tokens=max_tokens)
        else:
            answer = ("", "Model not supported.")

        new_chat = Chat(user_id=user_id, question=new_prompt, answer=answer[1], model=selected_model)
        db.session.add(new_chat)
        db.session.commit()

    # Reload recent chat history
    chat_history = Chat.query.filter_by(user_id=user_id).order_by(Chat.id.desc()).limit(10).all()
    chat_history.reverse()

    return render_template(
        'Prompt-area.html',
        name=current_user.name,
        chat_history=chat_history,
        system_prompts=system_prompts,
        selected_system_prompt_id=system_prompt_id,
        selected_model=selected_model
    )


@main.route('/modification', methods=["GET", "POST"])
@login_required
def modifier():
    """
    System prompt management:
    - Create, update, list system prompts used as context for models
    """
    if request.method == "POST":
        prompt_id = request.form.get("id")
        role = request.form.get("role")
        content = request.form.get("content")
        temperature = float(request.form.get("temperature", 0.7))
        max_tokens = int(request.form.get("max_tokens", 150))

        if prompt_id:
            prompt = SystemPrompt.query.get(prompt_id)
            if prompt:
                prompt.role = role
                prompt.content = content
                prompt.temperature = temperature
                prompt.max_tokens = max_tokens
        else:
            prompt = SystemPrompt(
                role=role,
                content=content,
                temperature=temperature,
                max_tokens=max_tokens
            )
            db.session.add(prompt)

        db.session.commit()
        return redirect(url_for('main.modifier'))

    edit_id = request.args.get("id")
    prompt_to_edit = SystemPrompt.query.get(edit_id) if edit_id else None
    prompts = SystemPrompt.query.all()
    return render_template("modifier.html", prompts=prompts, prompt_to_edit=prompt_to_edit)


@main.route('/modification/delete/<int:id>', methods=["POST"])
@login_required
def delete_prompt(id):
    """Delete a system prompt by id."""
    prompt = SystemPrompt.query.get(id)
    if prompt:
        db.session.delete(prompt)
        db.session.commit()
    return redirect(url_for('main.modifier'))


# NOTE: Remove or comment this line if you don't want to load a text file index at startup
# ollama_rag.build_index_from_file('cat-facts.txt')


@main.route('/rag', methods=['GET', 'POST'])
@login_required
def rag_route():
    """Simple RAG interface with Ollama-based answer generation."""
    answer = None
    if request.method == 'POST':
        user_query = request.form.get('query')
        if user_query:
            answer = ollama_rag.generate_answer(user_query)
    return render_template('rag.html', answer=answer)


@main.route('/pimp-it', methods=['GET', 'POST'])
@login_required
def pimp_it():
    answer = None

    uploaded_files = [
        f for f in os.listdir(UPLOAD_FOLDER)
        if f.lower().endswith('.pdf')
    ]

    if request.method == 'POST':
        # Neue PDF hochladen und indexieren
        if 'pdf_file' in request.files and request.files['pdf_file'].filename:
            file = request.files['pdf_file']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                filepath = os.path.join(UPLOAD_FOLDER, filename)
                os.makedirs(UPLOAD_FOLDER, exist_ok=True)
                file.save(filepath)
                ollama_rag.build_index_from_pdf(filepath)
                ollama_rag.save_vector_db(filepath)  # <-- Speichern des Vektorindex

        # Bestehende PDF auswählen und Vektorindex laden
        elif request.form.get('selected_pdf'):
            selected_pdf = request.form.get('selected_pdf')
            filepath = os.path.join(UPLOAD_FOLDER, selected_pdf)
            if os.path.exists(filepath):
                ollama_rag.load_vector_db(filepath)

        # Nutzeranfrage beantworten
        user_query = request.form.get('query')
        if user_query:
            answer = ollama_rag.generate_answer(user_query)

    return render_template(
        'pimp-it.html',
        answer=answer,
        uploaded_files=uploaded_files
    )