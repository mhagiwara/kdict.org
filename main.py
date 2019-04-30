from flask import Flask, render_template

app = Flask(__name__)

@app.route('/health')
def health():
    return "alive"

@app.route('/')
def home():
    return render_template('index.html')

if __name__ == '__main__':
    if os.environ['ENVIRONMENT'] == 'production':
        app.run(port=80, host='0.0.0.0')
    if os.environ['ENVIRONMENT'] == 'local':
        app.run(port=5000, host='0.0.0.0')
