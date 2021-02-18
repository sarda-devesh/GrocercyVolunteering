from twilio.rest import Client
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import threading

twillio_phone_number = "[Number]"
account_sid = "[SID]"
auth_token = "[TOKEN]"
client = Client(account_sid, auth_token)

def send_message(phone_number, message):
    client.messages.create(from_= twillio_phone_number, to = phone_number, body = message)

app = Flask(__name__)
@app.route('/sms', methods=['POST'])
def sms():
    temp_lock = threading.Lock()
    with temp_lock:
        resp = MessagingResponse()
        number = request.form['From']
        message_body = request.form['Body']
        resp.message('Hello {}, you said: {}'.format(number, message_body))
        if "close" in message_body.lower():
            print("User requested close")
            raise RuntimeError("User requested shutdown")
        return str(resp)

def process_runner():
    app.run(host = '0.0.0.0',port = 5000)

if __name__ == '__main__':
    incoming = threading.Thread(target=process_runner)
    print("Starting application")
    incoming.start()
    while(True):
        user_number = raw_input("Please enter the phone number: ")
        user_message = raw_input("Please enter a message: ")
        if "close" in user_message.lower():
            print("User invoked exit")
            send_message(user_number, user_message)
            break
    incoming.join()
