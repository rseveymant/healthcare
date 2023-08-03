from flask import render_template, request, send_file
from .utils.gpt_service import GPTService
from .utils.code_mapper import ICD10Generator
import io
from io import BytesIO
import os
from dotenv import load_dotenv

load_dotenv()
MANTIUM_CLIENT_ID = os.getenv("MANTIUM_CLIENT_ID")
MANTIUM_SECRET = os.getenv("MANTIUM_SECRET")

gpt_service = GPTService()
icd10_generator = ICD10Generator(MANTIUM_CLIENT_ID, MANTIUM_SECRET, gpt_service)

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

    @app.route('/generate_billing_codes', methods=['GET', 'POST'])
    def generate_billing_codes():
        if request.method == 'POST':
            diagnosis = request.form.get('diagnosis', '')
            procedures = request.form.get('procedures', '')
            medical_history = request.form.get('medical_history', '')
            clinical_notes = request.form.get('clinical_notes', '')

            # Prepare the initial GPT prompt
            initial_prompt = f"Combine the following information into a good query to find the right ICD-10 code. The query will be sent to a vector database:\n\nDiagnosis: {diagnosis}\nProcedures: {procedures}\nMedical History: {medical_history}\nClinical Notes: {clinical_notes}"

            # Generate a query for Mantium RAG model
            rag_query = gpt_service.generate(initial_prompt)

            # Generate a billing code from the query
            billing_code = icd10_generator.generate(rag_query)

            # Render the results
            return render_template('billing_codes.html', billing_code=billing_code)

        return render_template('billing_codes_form.html')