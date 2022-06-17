from flask import Flask
from helpers.ping_helper import ping_statistics

app = Flask(__name__)


@app.route('/')
def hello():
    return 'Everything is proceeding normally.'


@app.route('/heartbeat', methods=["GET"])
def heartbeat():
    ping_data = ping_statistics()
    response = app.response_class(
        response=ping_data,
        status=200,
        mimetype='application/json'
    )
    return response


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
