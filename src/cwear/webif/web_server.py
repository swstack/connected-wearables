import os
from flask import Flask, render_template

app = Flask(__name__, static_url_path="")

HAPI_CLIENT_ID = os.environ.get('HAPI_CLIENT_ID')

@app.route('/')
def index():
    return render_template('index.html', hapi_client_id=HAPI_CLIENT_ID)

@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')

if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)