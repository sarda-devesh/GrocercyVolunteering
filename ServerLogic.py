import os
from twilio.rest import Client
from flask import Flask, request
from twilio import twiml

twillio_phone_number = "[Number]"
account_sid = "[SID]"
auth_token = "[TOKEN]"
HOST = '172.31.39.142'
PORT = 6666
BUFFER_SIZE = 4096
threads = []
users = {}

app = Flask(__name__)
@app.route('/sms', methods=['POST'])
def sms():
    number = request.form['From']
    message_body = request.form['Body']

def send_message(phone_number, message):
    client = Client(account_sid, auth_token)
    client.messages.create(from_= twillio_phone_number, to = phone_number, body = message)
    print(message.sid)

def client_processor(socket, address):
        socket.settimeout(None)
        incoming_message = ""
        while(True):
            try:
                part = socket.recv(BUFFER_SIZE).decode().strip()
                incoming_message += part
                if ";" in part:
                    index = incoming_message.index(";")
                    incoming_message = incoming_message[:index].split(",")
                    socket.close()
                    break
            except Exception as e:
                socket.sendall("There was an error".encode())
                    

current_directory = os.getcwd()
directories_to_make = [os.path.join(current_directory, "Users"), os.path.join(current_directory, "Volunteers")]
for directory in directories_to_make:
    if not os.path.exists(directory):
        os.mkdir(directory)
        
app.run()
serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind((HOST, PORT))
serversocket.settimeout(timeout)
serversocket.listen()

while(True):
    try:
        socket,address = serversocket.accept()
        print("Connected to " + str(address))
        current_thread = threading.Thread(target = client_processor,args = (socket, address, ))
        current_thread.start()
        threads.append(current_thread)
        timeout_count = 0
    except Exception as e:
        error_name = str(e).strip()
        if(error_name == "timed out"):
            continue
        else:
            print("There was an error: " + str(e))
            break
