from flask import Flask, request, jsonify
import os
from maestro import generate_pdf, generate_audio_from_text, extract_text_from_pdf
from twilio_api import send_message, send_language_preference_template, send_audiobook_preference_template, send_audiobook

app = Flask(__name__)

# A simple in-memory storage for user objectives and preferences
user_objectives = {}
user_language_preferences = {}
user_audio_preferences = {}


@app.route('/')
def home():
    return jsonify({
        'status': 'OK',
        'webhook_url': 'BASEURL/twilio/receiveMessage',
        'message': 'The webhook is ready.',
        'video_url': 'https://youtu.be/y9NRLnPXsb0'
    })


@app.route('/twilio/receiveMessage', methods=['POST'])
def receive_message():
    try:
        message_body = request.form['Body']
        sender_id = request.form['From']

        if message_body.strip().lower() == 'ok':
            return 'OK', 200
        
        if sender_id in user_objectives:
            if sender_id in user_language_preferences:
                if message_body.lower() in ['yes', 'no']:
                    # Store audio preference and generate PDF
                    user_audio_preferences[sender_id] = message_body.lower(
                    ) == 'yes'
                    use_search = True  # Set this based on your requirements
                    language_preference = user_language_preferences.pop(
                        sender_id)
                    objective = user_objectives.pop(sender_id)
                    result = generate_pdf(objective, use_search,
                                          language_preference)

                    # Translate message if necessary
                    if language_preference == 'hinglish':
                        translated_message = "यहाँ पीडीएफ फाइल है:"
                    else:
                        translated_message = "Here is the PDF file:"

                    # Send the translated message with the PDF link
                    send_message(sender_id, translated_message, result)

                    # Send audiobook if preferred
                    if user_audio_preferences.pop(sender_id, False):
                        print(f"User {sender_id} prefers audiobook.")
                        pdf_text = extract_text_from_pdf(result)
                        print(
                            f"Extracted text from PDF: {pdf_text[:50]}..."
                        )  # Print the first 50 characters of the extracted text
                        audiobook_url = generate_audio_from_text(pdf_text)
                        print(f"Audiobook URL: {audiobook_url}")
                        if language_preference == 'hinglish':
                            translated_message = "यहाँ ऑडियोबुक फाइल है:"
                        else:
                            translated_message = "Here is the audiobook file:"
                        send_audiobook(sender_id, translated_message,
                                       audiobook_url)
                else:
                    # Ask for valid audio preference again
                    send_audiobook_preference_template(sender_id)
            else:
                if message_body.lower() in ['english', 'hinglish']:
                    # Store language preference and ask for audio preference
                    user_language_preferences[sender_id] = message_body.lower()
                    send_audiobook_preference_template(sender_id)
                else:
                    # Ask for valid language preference again
                    send_language_preference_template(sender_id)
        else:
            # Store the objective and ask for language preference
            user_objectives[sender_id] = message_body
            send_language_preference_template(sender_id)

    except Exception as e:
        print(f"Error: {str(e)}")
        return 'Error', 500

    return 'OK', 200


if __name__ == '__main__':
    app.run(debug=True)
