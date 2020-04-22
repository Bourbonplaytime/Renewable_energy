from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route('/')
def view():
    return render_template("index.html")

@app.route('/<name>')
def index(name='Energy'):
    return "Renewable {} Statistics".format(name)

app.run(debug=True, port=8000, host='0.0.0.0')
