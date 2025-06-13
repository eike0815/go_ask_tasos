from flask import Blueprint, render_template, request,session,  jsonify, redirect, url_for, send_file, make_response
from flask_login import login_required, current_user
from . import db
from project import grogmodel, chatgptmodel
from .models import Chat, User

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/Prompt-area', methods=["POST", "GET"])
@login_required
def prompt_area():
    user_id = current_user.id
    selected_model = request.args.get("modell", "grog")
    new_prompt = request.args.get('prompt')
    #new_chat = Chat(user_id= user_id, question= new_prompt)
    if new_prompt:
        if selected_model == "grog":
            # chatgptmodel.chat_answers_question(new_prompt)
            answer = grogmodel.give_answer(new_prompt)
        elif selected_model =="chatgpt":
            answer = chatgptmodel.chat_answers_question(new_prompt)
        new_chat = Chat(user_id=user_id, question=new_prompt, answer=answer[1], model=selected_model)
        db.session.add(new_chat)
        db.session.commit()
    chat_history= Chat.query.filter_by(user_id=user_id).order_by(Chat.id.asc()).all()
    print(selected_model)
    return render_template('Prompt-area.html', name=current_user.name, chat_history = chat_history)
