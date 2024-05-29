import os
from twilio.rest import Client
import json

# Twilio credentials
account_sid = os.getenv('TWILIO_SID')
auth_token = os.getenv('TWILIO_TOKEN')
client = Client(account_sid, auth_token)
content_sid = "HXaa90b0d854819db69d01a0072e71f980"
messaging_service_sid = 'MG979591b36608119df4ee935b79a9ec4a'
audio_content_sid = "HX3fd0f5717e5bc35ad38e87b4e8af4604"


def send_message(to: str, message: str, media_url) -> None:
    '''
    Send message to a WhatsApp user.
    Parameters:
        - to(str): recipient WhatsApp number in this format: whatsapp:+919558515995
        - message(str): text message to send
        - media_url(str, optional): URL of media to send
    Returns:
        - None
    '''
    try:
        print(f"Sending message to: {to}")
        print(f"Message: {message}")
        if media_url:
            print(f"Media URL: {media_url}")

        client.messages.create(from_='whatsapp:+15162727047',
                               body=message,
                               to=to,
                               media_url=[media_url] if media_url else None)

        print("Message sent successfully.")
    except Exception as e:
        print(f"Error sending message: {str(e)}")


def send_language_preference_template(to: str) -> None:
    try:
        print(f"Sending language preference template to: {to}")
        client.messages.create(
            content_sid=content_sid,
            from_=messaging_service_sid,
            to=to,
            content_variables=json.dumps(
                {"1": "Name"})  # Adjust the content variables as needed
        )
        print("Language preference template sent successfully.")
    except Exception as e:
        print(f"Error sending language preference template: {str(e)}")


def send_audiobook_preference_template(to: str) -> None:
    try:
        print(f"Sending audio preference template to: {to}")
        client.messages.create(
            content_sid=audio_content_sid,
            from_=messaging_service_sid,
            to=to,
            content_variables=json.dumps(
                {"1": "Name"})  # Adjust the content variables as needed
        )
        print("Audio preference template sent successfully.")
    except Exception as e:
        print(f"Error sending audio preference template: {str(e)}")


def send_audiobook(to: str, message: str, audiobook_url) -> None:
    '''
    Send an audiobook to a WhatsApp user.
    Parameters:
        - to(str): recipient WhatsApp number in this format: whatsapp:+919558515995
        - message(str): text message to send with the audiobook
        - audiobook_url(str): URL of the audiobook to send
    Returns:
        - None
    '''
    try:
        print(f"Sending audiobook to: {to}")
        print(f"Message: {message}")
        print(f"Audiobook URL: {audiobook_url}")

        client.messages.create(from_='whatsapp:+15162727047',
                               body=message,
                               to=to,
                               media_url=[audiobook_url])

        print("Audiobook sent successfully.")
    except Exception as e:
        print(f"Error sending audiobook: {str(e)}")


# Example usage (uncomment for testing):
# send_message('whatsapp:+1234567890', 'Hello, this is a test message!', 'https://example.com/media.pdf')
# send_language_preference_template('whatsapp:+1234567890')
