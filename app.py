from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from google import genai
import re

import os
from dotenv import load_dotenv

##load_dotenv()  # Load variables from .env file
Api_key = os.environ.get("API_KEY")

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Add a secret key for session management
CORS(app)

@app.route('/')
def homepage():
    return render_template('homepage.html')

@app.route('/homepage')
def homepage():
    return render_template('homepage.html')

@app.route('/loginpage')
def login():
    return render_template('Loginpage.html')

client = genai.Client(api_key = Api_key)


@app.route("/Chatpage", methods=["GET", "POST"])
def chatpage():
    # Initialize chat history if it doesn't exist in session
    if 'chat_history' not in session:
        session['chat_history'] = []
    
    if request.method == "POST":
        user_message = request.form.get("message")  # Get user input
        model_option = request.form.get("model")
        
        if user_message:
            # Add user message to chat history
            session['chat_history'].append({"role": "user", "content": user_message})
            
            if model_option == "SmartSaver":
                try:
                    # First response - Investment options
                    investment_response = ""
                    investment_query = client.models.generate_content_stream(
                        model="gemini-2.0-flash",
                        contents=["Someone wants to buy " + user_message + ". List 3 investment options instead for that amount of money. Be concise."]
                    )
                    for chunk in investment_query:
                        investment_response += chunk.text
                    
                    # Add investment options to chat history
                    session['chat_history'].append({
                        "role": "assistant", 
                        "content": "💼 Investment Alternatives:\n" + investment_response
                    })
                    
                    # Second response - Cheaper alternatives
                    cheaper_response = ""
                    cheaper_query = client.models.generate_content_stream(
                        model="gemini-2.0-flash",
                        contents=["Someone wants to buy " + user_message + ". List 3 alternative cheaper options for this item. Be concise."]
                    )
                    for chunk in cheaper_query:
                        cheaper_response += chunk.text
                    
                    # Add cheaper alternatives to chat history
                    session['chat_history'].append({
                        "role": "assistant", 
                        "content": "💰 Budget-Friendly Alternatives:\n" + cheaper_response
                    })
                    
                    session.modified = True  # Make sure session is saved
                    
                    # Return both responses for display
                    return render_template(
                        "Chatpage.html", 
                        investment_response="💼 Investment Alternatives:\n" + investment_response,
                        cheaper_response="💰 Budget-Friendly Alternatives:\n" + cheaper_response,
                        chat_history=session.get('chat_history')
                    )
                    
                except Exception as e:
                    error_message = f"Error: {str(e)}"
                    session['chat_history'].append({"role": "assistant", "content": error_message})
                    session.modified = True
                    return render_template("Chatpage.html", response=error_message, chat_history=session.get('chat_history'))
            
            elif model_option == "GenQ":
                try:
                    # Generate AI response for GenQ
                    ai_response = ""
                    response = client.models.generate_content_stream(
                        model="gemini-2.0-flash",
                        contents=["Make the response concise " + user_message]
                    )
                    for chunk in response:
                        ai_response += chunk.text
                    
                    # Add AI response to chat history
                    session['chat_history'].append({"role": "assistant", "content": ai_response})
                    session.modified = True  # Make sure session is saved
                    return render_template("Chatpage.html", response=ai_response, chat_history=session.get('chat_history'))
                
                except Exception as e:
                    error_message = f"Error: {str(e)}"
                    session['chat_history'].append({"role": "assistant", "content": error_message})
                    session.modified = True
                    return render_template("Chatpage.html", response=error_message, chat_history=session.get('chat_history'))
    
    # For GET requests or if no message was submitted
    return render_template("Chatpage.html", chat_history=session.get('chat_history'))

@app.route('/reset_chat', methods=["POST"])
def reset_chat():
    if 'chat_history' in session:
        session.pop('chat_history')
    return jsonify({"status": "success"})

@app.route('/badges')
def badges():
    return render_template('badges.html')

if __name__ == '__main__':
    app.run(debug=True)
