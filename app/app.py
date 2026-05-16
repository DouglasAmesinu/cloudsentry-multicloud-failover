from flask import Flask, jsonify
import socket, os

app = Flask(__name__)

@app.route('/')
def index():
    return jsonify({
        'status': 'ok',
        'host': socket.gethostname(),
        'provider': os.environ.get('PROVIDER', 'unknown'),
        'region': os.environ.get('REGION', 'unknown'),
        'message': 'CloudSentry multicloud failover demo'
    })

@app.route('/health')
def health():
    return jsonify({'status': 'healthy'}), 200

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
