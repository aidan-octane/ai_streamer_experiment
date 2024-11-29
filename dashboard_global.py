from flask import Flask, render_template
from flask_socketio import SocketIO, emit
import os 
from chatget import chatget
import threading
import time
import queue
import requests
import jsonify
from pyngrok import ngrok
from transformers import AutoTokenizer
from keys import broadcaster_id, auth_token, user_id, client_id, headers, API_URL

print("Code began!")
secret_key = os.urandom(16)
app = Flask(__name__)
app.config['SECRET_KEY'] = str(secret_key)
socketio = SocketIO(app)

input_queue = queue.Queue()
output_queue = queue.Queue()

EOS_TOKEN = AutoTokenizer.from_pretrained("tachophobicat/tachophobicai_v4.0").eos_token




# alpaca_prompt = """Respond to the input as if you were a Twitch streamer talking to your chat. Your name is Aidan Tachophobicat and you tend to go on entertaining rambles.

# ### Input:
# {input}

# {optional_fields}

# ### Response:
# {response}
# """

alpaca_prompt = """You are Aidan Tachophobicat, a Twitch streamer known for being entertaining and rambling. You are currently live on stream talking to an audience. {input} {optional_fields} {EOS_TOKEN} ### Response: {response}"""

#####################################################################################################
# AI STUFF # 
def query(payload):
	response = requests.post(API_URL, headers=headers, json=payload)
	return response.json()


def model_infer(user_input, type):
    type = str(type)
    if type == "chat":
        unformatted_model_input = {
        "input": "Generate a response to the chat message. ### Message: ",
        # "input": "Generate a response to the chat message. ",

        "message": user_input,
        "command": None,
        "prompt": None
        }
    elif type == "admin_command":
        unformatted_model_input = {
        # "input": "Generate a natural response to the given command, as you would say it on stream. ",
        "input": "Generate a natural response to the given command, as you would say it on stream. ### Command: ",
        "message": None,
        "command": user_input,
        "prompt": None
        }
    elif type == "monologue":
        unformatted_model_input = {
        # "input": "Generate a long, rambling monologue relating to the given prompt. ",
        "input": "Generate a long, rambling monologue relating to the given prompt. ### Prompt: ",
        "message": None,
        "command": None,
        "prompt": user_input
        }
    else:
        print("Could not determine what type of input was necessary - received " + type)
        return ("output error")
    
    # Formatting "alpaca prompt"
    optional_fields = ""
    if unformatted_model_input["message"]:
        optional_fields += str({unformatted_model_input['message']})
    if unformatted_model_input["command"]:
        optional_fields += str({unformatted_model_input['command']})
    if unformatted_model_input["prompt"]:
        optional_fields += str({unformatted_model_input['prompt']})
    model_input = alpaca_prompt.format(
            input=unformatted_model_input["input"],
            EOS_TOKEN = EOS_TOKEN,
            optional_fields=optional_fields,
            response=""
        )
    model_input = model_input
    model_input = model_input.replace('"', '').replace('\'', '')
    print("Sending " + model_input)
    payload = {
        "inputs": model_input,
        "parameters": {"temperature": 0.9}
    }
    api_response = query(payload)

    # print(str(api_response))
    # formatted_response = api_response.get("generated_text", "")
    formatted_response = str(api_response)
    print(formatted_response)
    response_index = formatted_response.rfind("Response:")
    if(response_index < 0):
        response_index = -9
    return formatted_response[response_index + 10:-3]
        
#######################################################################################################

# Blocklist - saved & dynamically updated
blocklist = []
with open(os.path.join(os.path.dirname(__file__), 'blocklist.txt'), 'r') as file:
    for line in file:
        blocklist.append(str(line)[:-1])
message_length_minimum = 10
messages_per_gen = 2
print("Current blocklist: " + str(blocklist))

def get_chat_messages():
    chatget.run_chat_server(broadcaster_id, auth_token, user_id, client_id)
    print("Chat loop beginning")
    i = 1
    while True:
        msg = chatget.get_next_chat()
        if(msg is not None): 
            print(msg)
            print("i = " + str(i) + ", threshold = " + str(messages_per_gen))
            if(i == messages_per_gen):
                print("i = " + str(i) + ", threshold = " + str(messages_per_gen))
                i = 0
                username = msg.split(":")[0]
                message = msg.split(":", 1)[1][1:]
                print("message length - " + str(len(message)) + ", threshold = " + str(message_length_minimum))
                if(username not in blocklist and len(message) > message_length_minimum):
                    model_response = model_infer(message, "chat")
                    send_to_frontend(msg, model_response)
                else: 
                    print("username found in blocklist and/or length min not met!")
            if i > messages_per_gen:
                i = 0
            i+=1
        time.sleep(1)





def send_to_frontend(msg, output):
    socketio.emit('update_message_content', {'text': msg})
    socketio.emit('update_message_content', {'text': output})



@app.route('/')
def index():
    return render_template('index.html')

# Handles input from dashboard itself
@socketio.on('submit_message')
def handle_input(data):
    input = data['text']
    command_type, command_body = input.split(":", 1)
    if command_type == "chat_response":
        command_type = "chat"
    output = model_infer(command_body, command_type)
    emit('update_command_content', {'text': input}, broadcast=True)
    emit('update_command_content', {'text': output}, broadcast=True)

# handles adding to blocklist
@socketio.on('submit_blocklist')
def handle_blocklist(data):
    data = data['text']
    print("Handle blocklist received " + str(data))
    # writes additional blocked username to file
    data = str(data)
    with open(os.path.join(os.path.dirname(__file__), 'blocklist.txt'), 'a') as file:
        file.write(f"{data}\n")
    blocklist.append(data)
    emit('update_command_content', {'text': 'Added \"' + str(data) + '\" to blocklist'})


@socketio.on('submit_gen_rate')
def handle_gen_rate(data):
    data = data['text']
    print("Handle gen rate received " + str(data))
    global messages_per_gen
    try:
        data = int(data)
        if data > 0:
            messages_per_gen = data
            emit('update_command_content', {'text': 'Added ' + str(data) + ' as new gen_rate'})

    except Exception as e:
        emit('update_command_content', {'text': 'Error adding ' + str(data) + ' as new gen_rate'})
        print("ERROR ADDING " + str(data) + " AS NEW GEN RATE")

@socketio.on('submit_char_threshold')
def handle_char_threshold(data):
    data = data['text']
    print("Handle char threshold received: " + str(data))
    global message_length_minimum
    try:
        data = int(data)
        message_length_minimum = int(data)
        emit('update_command_content', {'text': 'Added ' + str(data) + ' as new char threshold (min characters for a msg to be generated)'})
    except Exception as e:
        emit('update_command_content', {'text': 'Error adding ' + str(data) + ' as new char threshold'})
        print("ERROR ADDING " + str(data) + " AS NEW CHAR THRESHOLD")


chat_history = []
admin_history = []

@app.route('/submit_admin', methods=['POST'])
def update_admin():
    data = requests.json['input']
    admin_history.append(data)
    return jsonify({'status': '400'})

@app.route('/submit_chat', methods=['POST'])
def update_chat():
    data = requests.json['input']
    chat_history.append(data)
    return jsonify({'status': '400'})

@app.route("/admin_history", methods=['GET'])
def get_admin_history():
    return jsonify({'history': admin_history})


@app.route("/chat_history", methods=['GET'])
def get_chat_history():
    return jsonify({'history': chat_history})

if __name__ == '__main__':
    public_url = ngrok.connect(5000)
    public_url = str(public_url)
    print("NGROK  URL: " + public_url)
    get_chat_thread = threading.Thread(target = get_chat_messages)
    get_chat_thread.daemon = True
    get_chat_thread.start()
    print("Starting server!")
    socketio.run(app, debug=False)
    emit('get_ngrok', {"url": str(public_url)})


