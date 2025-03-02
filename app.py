from flask import Flask, request, jsonify, render_template, session
from flask_cors import CORS
from google import genai
import re

app = Flask(__name__)
app.secret_key = "your_secret_key_here"  # Add a secret key for session management
CORS(app)

@app.route('/homepage')
def homepage():
    return render_template('homepage.html')

@app.route('/loginpage')
def login():
    return render_template('Loginpage.html')

client = genai.Client(api_key="AIzaSyBIvKviwbeNVPKqxSAT1QlZbOxLq1-_pXE")

@app.route("/Chatpage", methods=["GET", "POST"])
def chatpage():
    # Initialize chat history if it doesn't exist in session
    if 'chat_history' not in session:
        session['chat_history'] = []
    
    ai_response = ""  # Initialize as empty string
    
    if request.method == "POST":
        user_message = request.form.get("message")  # Get user input
        
        if user_message:
            try:
                # Add user message to chat history
                session['chat_history'].append({"role": "user", "content": user_message})
                
                # Generate AI response
                response = client.models.generate_content_stream(
                    model="gemini-2.0-flash",
                    contents=["Someone wants to buy " + user_message + " . List 3 investment options instead for that amount of money and 3 alternative cheaper options for the thing they are buying. Give a concise response"])
                
                for chunk in response:
                    ai_response += chunk.text
                
                # Format the response: Add a newline before "Cheaper"
                ai_response = re.sub(r'(Cheaper)', r'\n\1', ai_response, flags=re.IGNORECASE)
                
                # Add AI response to chat history
                session['chat_history'].append({"role": "assistant", "content": ai_response})
                session.modified = True  # Make sure session is saved
                
            except Exception as e:
                ai_response = f"Error: {str(e)}"
    
    # For GET requests or after processing POST, render the template
    return render_template("Chatpage.html", response=ai_response, chat_history=session.get('chat_history'))

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
