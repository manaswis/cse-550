from flask import Flask
from flask import render_template

app = Flask(__name__)

@app.route("/<name>")
def server(name='user1'):
    return render_template('tool.html', name=name)
