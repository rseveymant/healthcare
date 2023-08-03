from flask import render_template, request, send_file
from .utils.gpt_service import GPTService
import io
from io import BytesIO

gpt_service = GPTService()

def setup_routes(app):
    @app.route('/', methods=['GET', 'POST'])
    def generate_text():
        response = ''
        if request.method == 'POST':
            prompt = request.form.get('prompt', '')
            response = gpt_service.generate(prompt)
        return render_template('index.html', response=response)

    @app.route('/prior_auth', methods=['GET', 'POST'])
    def prior_auth():
        if request.method == 'POST':
            patient_info = request.form.get('patient_info', '')
            treatment_plan = request.form.get('treatment_plan', '')
            
            # Combine patient_info and treatment_plan into a single prompt.
            # Modify this according to your needs
            prompt = f"Create a medial Prior Authorization request based on the following: Patient information: {patient_info}\nTreatment Plan: {treatment_plan}"
            
            # Generate prior authorization document text
            document_text = gpt_service.generate(prompt)
            
            # Convert text to a file
            mem = BytesIO()
            mem.write(document_text.encode('utf-8'))
            mem.seek(0)
            
            # Send file
            return send_file(mem, as_attachment=True, download_name='prior_authorization.txt', mimetype='text/plain')

        return render_template('prior_auth_form.html')