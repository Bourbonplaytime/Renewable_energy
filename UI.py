import json
from flask import Flask, render_template, redirect, url_for, request, make_response

app = Flask(__name__)

def get_saved_data():
    try:
        data = json.loads(request.cookies.get('visuals'))
    except TypeError:
        data = {}
    return data

@app.route('/')
def index():
    data = get_saved_data()
    return render_template("index.html", saves=get_saved_data())

@app.route('/show', methods=['POST'])
def show():
    response = make_response(redirect(url_for('index')))
    data = get_saved_data()
    data.update(dict(request.form.items()))
    response.set_cookie('visuals', json.dumps(data))
    return response

app.run(debug=True, port=8000, host='0.0.0.0')
