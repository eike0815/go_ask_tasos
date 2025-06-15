from flask import Blueprint, render_template, request,session,  jsonify, redirect, url_for, send_file, make_response
from flask_login import login_required, current_user
from . import db
from project import grogmodel, chatgptmodel
from .models import Chat, User, SystemPrompt

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')
@main.route('/Prompt-area', methods=["POST", "GET"])
@login_required
def prompt_area():
    user_id = current_user.id

    # Eingaben aus GET/POST
    selected_model = request.args.get("modell", "grog")
    new_prompt = request.args.get("prompt")
    system_prompt_id = request.args.get("system_prompt_id")  # NEU

    # Chat-Historie abrufen
    chat_history = Chat.query.filter_by(user_id=user_id).order_by(Chat.id.asc()).all()

    # Alle verfügbaren Systemprompts laden (für Dropdown)
    system_prompts = SystemPrompt.query.all()

    # Prompt auswählen (wenn ID vorhanden)
    selected_system_prompt = SystemPrompt.query.get(system_prompt_id) if system_prompt_id else None

    # Defaults setzen (wenn nichts gewählt wurde)
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

    # Wenn ein neuer Prompt vom Nutzer eingegeben wurde
    if new_prompt:
        # Letzten Kontext zusammensetzen
        context = ""
        for chat in chat_history[-20:]:
            context += f"User: {chat.question}\nAI: {chat.answer}\n"

        combined_prompt = context + f"User: {new_prompt}"

        # Modell aufrufen
        if selected_model == "grog":
            answer = grogmodel.give_answer(
                combined_prompt,
                system_prompt_override=system_msg,
                temperature=temperature,
                max_tokens=max_tokens
            )
        elif selected_model == "chatgpt":
            answer = chatgptmodel.chat_answers_question(
                combined_prompt,
                system_prompt_override=system_msg,
                temperature=temperature,
                max_tokens=max_tokens
            )

        # Ergebnis speichern
        new_chat = Chat(
            user_id=user_id,
            question=new_prompt,
            answer=answer[1],
            model=selected_model
        )
        db.session.add(new_chat)
        db.session.commit()

        chat_history = Chat.query.filter_by(user_id=user_id).order_by(Chat.id.asc()).all()

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
    if request.method == "POST":
        # Create or Update
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

    # Prüfen, ob eine ID zum Bearbeiten übergeben wurde
    edit_id = request.args.get("id")
    prompt_to_edit = SystemPrompt.query.get(edit_id) if edit_id else None

    prompts = SystemPrompt.query.all()
    return render_template("modifier.html", prompts=prompts, prompt_to_edit=prompt_to_edit)
@main.route('/modification/delete/<int:id>', methods=["POST"])
@login_required
def delete_prompt(id):
    prompt = SystemPrompt.query.get(id)
    if prompt:
        db.session.delete(prompt)
        db.session.commit()
    return redirect(url_for('main.modifier'))






@main.route('/pimp-it', methods=["POST", "GET"])
@login_required
def pimp_it():
    pass #rag, input knowledge by pdf