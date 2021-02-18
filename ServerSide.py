import socket
from queue import Queue
from twilio.rest import Client
from flask import Flask, request
from twilio.twiml.messaging_response import MessagingResponse
import threading
import os
from geopy.geocoders import Nominatim
from geopy.distance import geodesic
import time

current_directory = os.getcwd()
directories_to_make = [os.path.join(current_directory, "Users"), os.path.join(current_directory, "Volunteers")]
for directory in directories_to_make:
    if not os.path.exists(directory):
        os.mkdir(directory)

HOST = '172.31.91.199'
PORT = 6666
BUFFER_SIZE = 4096
threads = []
quit_queue = Queue()
twillio_phone_number = "[Number]"
account_sid = "[SID]"
auth_token = "[AUTH]"
client = Client(account_sid, auth_token)
app = Flask(__name__)

def process_user_response(message, user_number):
    message = message.lower()
    user_file = str(user_number) + '.txt'
    volunteer_number = ""
    if "no" in message:
        with open(os.path.join(directories_to_make[0], user_file), 'r+') as file:
            lines = file.read().splitlines()
            volunteer_number = lines[4]
            lines[4] = "None"
            file.seek(0)
            file.truncate()
            file.write("\n".join(lines))
        read_update_order(user_file)
    elif "done" in message:
        with open(os.path.join(directories_to_make[0], user_file), 'r') as file:
            lines = file.read().splitlines()
            volunteer_number = lines[4]
        file_path = str(os.path.join(directories_to_make[0], user_file))
        os.remove(file_path)
    if len(volunteer_number) < 2:
        return None
    with open(os.path.join(directories_to_make[1], volunteer_number), 'r+') as vol_file:
        lines = vol_file.read().splitlines()
        lines[3] = "None"
        vol_file.seek(0)
        vol_file.truncate()
        lines = "\n".join(lines)
        vol_file.write(lines)
        
def process_volunteer_response(message, volunteer_number):
    message = message.lower()
    volunteer_file = str(volunteer_number) + ".txt"
    if "yes" in message:
        user_number = ""
        volunteer_name = ""
        with open(os.path.join(directories_to_make[1], volunteer_file), 'r') as vol_file:
            lines = vol_file.read().splitlines()
            user_number = lines[3]
            volunteer_name = lines[0]
        message = " We have a volunteer named " + str(volunteer_name) + " who you can contact at " + str(volunteer_number) +".Reply with either No or Done!"
        send_message(user_number, message)
        with open(os.path.join(directories_to_make[0], user_number), 'r+') as user_file:
            lines = user_file.read().splitlines()
            lines[4] = volunteer_file
            user_file.seek(0)
            user_file.truncate()
            user_file.write("\n".join(lines))
    if "no" in message:
        user_number = ""
        with open(os.path.join(directories_to_make[1], volunteer_file), 'r+') as vol_file:
            lines = vol_file.read().splitlines()
            user_number = lines[3]
            lines[3] = "None"
            vol_file.seek(0)
            vol_file.truncate()
            lines = "\n".join(lines)
            vol_file.write(lines)
        read_update_order(user_number)

def read_update_order(user_number):
    with open(os.path.join(directories_to_make[0], user_number), 'r+') as user_file:
        lines = user_file.read().splitlines()
        order = lines[5:]
        for index in range(len(order)):
            one = order[index].split(",")
            order[index] = (one[0], float(one[1]))
        send_to_best_volunteer(order, user_number, lines[3])
        for index in range(len(order)):
            order[index] = str(order[index][0]) + "," + str(order[index][1])
        lines = lines[:5] + order
        to_write = "\n".join(lines)
        user_file.seek(0)
        user_file.truncate()
        user_file.write(to_write)
    

@app.route('/sms', methods=['POST', 'GET'])
def sms():
    temp_lock = threading.Lock()
    with temp_lock:
        resp = MessagingResponse()
        number = request.form['From']
        message_body = request.form['Body']
        if os.path.exists(directories_to_make[0], number):
            process_user_message(message_body, number)
        elif os.path.exists(directories_to_make[1], number):
            process_volunteer_message(message_body, number)

def send_message(phone_number, message):
    if '.' in phone_number:
        phone_number = phone_number[:phone_number.index('.')]
    print("Sending message " + str(message) + " to " + str(phone_number))
    #client.messages.create(from_= twillio_phone_number, to = phone_number, body = message)

#User file - 0 - name,1 - latitude, 2 - longitude, 3 - order, 4 - current, Volunteer list (vol_name, distance)
#Data - name, adress, order
#Vol_file - name, lat, long, current

def get_lat_long(adress):
    geolocator = Nominatim()
    location = geolocator.geocode(adress)
    return (location.latitude, location.longitude)

def send_to_best_volunteer(order, user_number, request):
    for index in range(len(order)):
            file_name = os.path.join(directories_to_make[1], order[index][0])
            with open(file_name, 'r+') as file:
                lines = file.read().splitlines()
                if(lines[3] == "None"):
                    print("The user number is " + str(user_number))
                    lines[3] = str(user_number) + '.txt' 
                    message = "We have an order of " + str(request) + " near you. Reply with Yes or No!"
                    volunteer = order.pop(index)
                    lines = "\n".join(lines)
                    file.seek(0)
                    file.truncate()
                    file.write(lines)
                    send_message(volunteer[0], message)
                    return True
    return False
    
def process_new_user(number, data):
    user_file_path = os.path.join(directories_to_make[0], number + ".txt")
    volunteer = directories_to_make[1]
    user_lat, user_long = get_lat_long(data[1])
    data = [str(data[0]), str(user_lat), str(user_long), str(data[2]), "None"]
    order = []
    for vol_filename in os.listdir(volunteer):
        with open(os.path.join(volunteer,vol_filename), 'r') as vol_file:
            lines = vol_file.read().splitlines()
            vol_lat, vol_long = float(lines[1]), float(lines[2])
            distance = geodesic((vol_lat, vol_long), (user_lat, user_long)).miles
            order.append((vol_filename, distance))
    order.sort(key = lambda arr:arr[1])
    sucess = send_to_best_volunteer(order, number, data[3])
    for index in range(len(order)):
        order[index] = str(order[index][0]) + "," + str(order[index][1])
    data = data + order
    with open(user_file_path, 'w+') as user_file:
        line_to_write = "\n".join(data)
        user_file.write(line_to_write)

def process_new_volunteer(number, data):
    vol_file_path = os.path.join(directories_to_make[1], number + ".txt")
    lat, long = get_lat_long(data[1])
    data = [str(data[0]), str(lat), str(long), "None"]
    with open(vol_file_path, 'w+') as vol_file:
        lines = "\n".join(data)
        vol_file.write(lines)
    for user_name in os.listdir(directories_to_make[0]):
        with open(os.path.join(directories_to_make[0], user_name), 'r+') as user_file:
            lines = user_file.read().splitlines()
            order = []
            if(len(lines) > 5):
                order = lines[5:]
            for index in range(len(order)):
                one = order[index].split(",")
                order[index] = (one[0], float(one[1]))
            user_lat, user_long = float(lines[1]), float(lines[2])
            distance = geodesic((lat, long), (user_lat, user_long)).miles
            order.append((number + ".txt", distance))
            order.sort(key = lambda arr:arr[1])
            if(len(order) == 1):
                send_to_best_volunteer(order, user_name, lines[3]) 
            for index in range(len(order)):
                order[index] = str(order[index][0]) + "," + str(order[index][1])
            lines = lines[:5] + order
            to_write = "\n".join(lines)
            user_file.seek(0)
            user_file.truncate()
            user_file.write(to_write)
            
def client_processor(socket, address):
        socket.settimeout(None)
        incoming_message = ""
        while(True):
            try:
                part = socket.recv(BUFFER_SIZE).decode().strip()
                incoming_message += part
                if ";" in incoming_message:
                    index = incoming_message.index(";")
                    display_message = incoming_message[:index]
                    incoming_message = incoming_message[index + 1:]
                    broken = display_message.split("/")
                    number = broken[1]
                    code = broken[0]
                    data = broken[2:]
                    if "0" in code:
                        process_new_volunteer(number, data)
                    if "1" in code:
                        process_new_user(number, data)
            except Exception as e:
                print("An error occured in method: " + str(e))
                quit_queue.put(str(address))
                socket.close()
                break
            
def process_runner():
    app.run(host = '0.0.0.0',port = 5000)

'''
incoming = threading.Thread(target=process_runner)
print("Starting Twilio listener application")
incoming.start()

serversocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
serversocket.bind((HOST, PORT))
serversocket.settimeout(timeout)
serversocket.listen()
print("Started socket listerner application")

while(True):
    if(quit_queue.qsize() >= len(threads) and quit_queue.qsize() > 0):
        break
    try:
        socket,address = serversocket.accept()
        print("Connected to " + str(address))
        current_thread = threading.Thread(target = client_processor,args = (socket, address, ))
        current_thread.start()
        threads.append(current_thread)
    except Exception as e:
        error_name = str(e).strip()
        if(error_name == "timed out"):
            print("Timeout error")
        else:
            print("There was a general error in base: " + str(error_name))
            break
for thread in threads:
    thread.join()
incoming.join()
serversocket.close()
'''

start = time.time()
process_user_response("DONE", "+14252467992")
print("That took " + str(time.time() - start))
