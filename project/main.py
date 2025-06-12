from flask import Blueprint, render_template, request, jsonify, redirect, url_for, send_file, make_response
from flask_login import login_required, current_user
from . import db

main = Blueprint('main', __name__)

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/Prompt-area', methods=["POST", "GET"])
@login_required
def prompt_area():
    prompt = request.args.get('prompt')
    print(prompt)
    return render_template('Prompt-area.html', name=current_user.name)