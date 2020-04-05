import telepot
from telepot.loop import MessageLoop
import cv2
import numpy as np
import json
import requests
import face_recognition as fr
import pickle

debug=False
if debug:
    from pprint import pprint

# globals
TOKEN = "1098884023:AAGNIUfqONpBZ47WKJ0LiVm-NDbQsXucneA"
FILE_URL = "https://api.telegram.org/bot{}/getFile?file_id={}"#token,file_id
IMAGE_URL = "https://api.telegram.org/file/bot{}/{}"#token,file_path
bot = telepot.Bot(TOKEN)
msg = None
last_encoding = None


# auxiliary functions
def update_pickle(new_encodings):
    chat_id = msg.get("chat").get("id")
    msg_id = msg_id = msg.get("message_id")
    filename = "encodings.pickle"

    # get encondings
    try:
        with open(filename, 'rb') as f:
            encodings = pickle.loads(f.read())
    except FileNotFoundError:
        encodings = ([],[])
    
    if debug:
        bot.sendMessage(chat_id, "Searching for matches...")
    find_text = "No match found."
    for new_encoding in new_encodings:
        matches = fr.compare_faces(encodings[0], new_encoding)

        # if no match is found
        found_msg_ids = []
        # if matches are found
        list_msg_id = [msg_id]
        if matches.count(True): 
            find_text = "Sending matches..."
            try:
                while True:
                    match_index = matches.index(True)
                    found_msg_ids = list_msg_id
                    print(encodings[1])
                    print(match_index)
                    list_msg_id += encodings[1][match_index]

                    matches[match_index] = False
                    encodings[0].remove(encodings[0][match_index])
                    encodings[1].remove(encodings[1][match_index])
            except ValueError:
                pass

        # update pickle
        encodings[0].append(new_encoding)
        encodings[1].append(list_msg_id)
        with open(filename, 'wb') as f:
            f.write(pickle.dumps(encodings))

    # find command
    if has_find_command():
        bot.sendMessage(chat_id, find_text)
        for id in found_msg_ids:
            bot.forwardMessage(chat_id,chat_id,id)


def get_image():
    file_id = msg.get("document").get("thumb").get("file_id")

    # get method image.jpg
    try:
        r = requests.get(FILE_URL.format(TOKEN, file_id))
        file_path = json.loads(r.text)["result"]["file_path"]
        r = requests.get(IMAGE_URL.format(TOKEN,file_path))
    except:
        raise Exception("request failed.")

    # jpg to np array
    image = np.asarray(bytearray(r.content), dtype="uint8")
    image = cv2.imdecode(image, cv2.IMREAD_COLOR)

    return image


# "has" functions
def has_find_command():
    command = "."
    return msg.get("caption") == command

def has_image():
    return  msg.get("document",{}).get("mime_type",'').startswith('image')


# handle functions
def handle_image():
    image = get_image()
    print(has_find_command())
    if debug and has_find_command():
        bot.sendMessage(msg.get("chat").get("id"),"Enconding faces...")
    new_encodings = fr.face_encodings(image)
    update_pickle(new_encodings)
    

def handle(received_msg):
    global msg
    msg = received_msg

    if debug:
        pprint(msg)
    
    if has_image():
        handle_image()    


# init function
def start():
    MessageLoop(bot, handle).run_forever()

if __name__ == "__main__":
    start()
    