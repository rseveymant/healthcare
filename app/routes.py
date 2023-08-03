from flask import render_template, request
from app import app
from app.utils.gpt_service import GPTService

gpt_service = GPTService()

@app.route('/', methods=['GET', 'POST'])
def generate_text():
    response = ''
    if request.method == 'POST':
        prompt = request.form.get('prompt', '')
        response = gpt_service.generate(prompt)
    return render_template('index.html', response=response)
