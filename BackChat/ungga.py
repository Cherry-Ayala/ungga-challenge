import re
from flask import Flask, request, jsonify
import torch
from flask_cors import CORS
from transformers import AutoModelForCausalLM, AutoTokenizer, pipeline
import firebase_admin
from firebase_admin import credentials, firestore

app = Flask(__name__)
CORS(app)

cred = credentials.Certificate("ungga-cfdf8-firebase-adminsdk-60fhy-653a80a6c6.json")
firebase_admin.initialize_app(cred)

db = firestore.client()

model_name = "gpt2"

try:
    model_path = model_name
    model = AutoModelForCausalLM.from_pretrained(model_path)
    tokenizer = AutoTokenizer.from_pretrained(model_path)
    generator = pipeline(
        'text-generation',
        model=model,
        tokenizer=tokenizer,
        device=0 if torch.cuda.is_available() else -1,
        temperature=0.7
    )

except Exception as e:
    print("Failed to access gpt2")
    exit()

# Data structure to store user information
user_info = {}

@app.route('/chat', methods=['POST'])
def chat():
    try:
        # Get user input from the frontend
        user_input = request.json['user_input']

        # Use NLP techniques for better information extraction
        # In this example, a simple regex is used. Replace it with more advanced NLP techniques if needed.
        match = re.search(r"(?i)name:\s*([^\n,]+).*?email:\s*([^\n,]+).*?phone:\s*([^\n,]+)", user_input)

        if match:
            # Extract information from the user input
            name = match.group(1).strip()
            email = match.group(2).strip()
            phone = match.group(3).strip()

            # Update user_info dictionary
            user_info = {'name': name, 'email': email, 'phone': phone}

            # Store information in Firebase
            appointment_data = {
                'name': name,
                'email': email,
                'phone': phone,
            }
            db.collection('appointments').add(appointment_data)

            # Generate a response using the GPT-2 model
            response = generator("Thank you! I have your information. Would you like to schedule an appointment now?", max_length=50, do_sample=True)[0]['generated_text']

            # Assuming user wants to schedule, proceed with scheduling
            if "yes" in response.lower():
                # Schedule the appointment using user_info
                scheduled_response = generator(f"Great! I will schedule an appointment for {name} on [date] at [time].", max_length=50, do_sample=True)[0]['generated_text']
                return jsonify({'response': scheduled_response})
            else:
                return jsonify({'response': "No problem! If you have any changes, feel free to provide the information again."})
        else:
            # If no scheduling information is provided, prompt the user for details
            response = generator("I'd like to schedule an appointment. Could you please provide your name, email, and phone number?", max_length=50, do_sample=True)[0]['generated_text']
            return jsonify({'response': response})

    except Exception as e:
        return jsonify({'error': str(e)})

if __name__ == '__main__':
    app.run(debug=True)

