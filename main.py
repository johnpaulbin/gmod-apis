from flask import Flask, request, jsonify
import os, glob, random, json
import requests
import urllib.parse
import banana_dev as banana
from threading import Thread


def choose_file():
    files = glob.glob(os.path.join(os.getcwd(), "Bible-kjv", "*.json"))
    return random.choice(files)


def get_verse():
    file = choose_file()
    with open(file, "r") as f:
        data = json.load(f)
        bookNAME = data["book"]
        chapter = random.choice(list(data["chapters"]))
        verse = random.choice(list(chapter["verses"]))
        verseNUM = verse["verse"]
        verseTEXT = verse["text"]
        return bookNAME, verseNUM, verseTEXT


def gpt_gen(text=None, length=20, temperature=0.9, topK=50, topP=0.95):
    model_parameters = {
            "text": text,
            "length": length,
            "temperature": temperature,
            "topK": topK,
            "topP": topP
        }
    return banana.run(api_key, "gptj", model_parameters)["modelOutputs"][0]["output"]
      
###############
# Flask app!
###############

app = Flask(__name__)
api_key = os.environ["banana"]


@app.route('/')
def hello_world():
    return 'GREETINGS'


@app.route('/bible')
def testpost():
    x, y, z = get_verse()
    return f"{x} {y}: {z}"


@app.route('/ip')
def ip():
    return str(request.environ['HTTP_X_FORWARDED_FOR'])


@app.route('/gpt/', methods=["POST"])
def gpt():
    try:
        if request.json != None:
            data = request.json
        else:
            try:
                data = json.loads(request.data)
            except:
                return 'data err'
              
        #print(data)
        if int(data["length"]) > 200:
            return 'length too long (200 max)'
        
        model_parameters = {
            "text": data["text"],
            "length": int(data["length"]),
            "temperature": float(data["temperature"]),
            "topK": int(data["topK"]),
            "topP": float(data["topP"])
        }
        #print(model_parameters)
        out = banana.run(api_key, "gptj", model_parameters)
        out = out["modelOutputs"][0]["output"]
        #print(out)
        try:
            return out.split(data["stop"])[0]
        except:
            return out
    except Exception as e:
        print(e)
        return 'error'


"""
@app.route('/gpt/<input>')
def gpt(input):
    url = 'https://api.textsynth.com/v1/engines/gptj_6B/completions'
    headers = {'content-type': 'application/json', 'Authorization': f'Bearer {os.environ["gptj"]}'}
    data = {
        'prompt': urllib.parse.unquote_plus(input),
        'temperature': 0.9,
        'top_k': 40,
        'top_p': .98,
        'stream': False,
        'max_tokens': 35
    }

    r = requests.post(url, data=json.dumps(data), headers=headers)
    return ''.join(json.loads(r.text)["text"])


@app.route('/einstein/<input>')
def einstein(input):
    url = 'https://api.textsynth.com/v1/engines/gptj_6B/completions'
    headers = {'content-type': 'application/json', 'Authorization': f'Bearer {os.environ["gptj"]}'}


    input = f'''Einstein: Hi, I'm Albert Einstein. I was born in March 14, 1879. What would you like to talk about today?
Person: What do you think about black holes?
Einstein: I personally denied several times that black holes could form. In 1939 I published a paper that argues that a star collapsing would spin faster and faster, but the concept itself is extremely fastinating and a topic I do want to talk more of.
Person: {urllib.parse.unquote_plus(input)}
Einstein:'''

    data = {
        'prompt': input,
        'temperature': 0.94,
        'top_k': 40,
        'top_p': 1.,
        'stream': False,
        'max_tokens': 177,
        'stop': 'Person:'
    }

    r = requests.post(url, data=json.dumps(data), headers=headers)
    return ''.join(json.loads(r.text)["text"])
"""
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
