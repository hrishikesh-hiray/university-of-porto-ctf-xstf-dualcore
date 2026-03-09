from flask import Flask, request, jsonify
import logging

app = Flask(__name__)

with open('flag.txt', 'r') as f:
    FLAG = f.read()
    f.close()

# LOGS
logging.basicConfig(
    filename='/tmp/app.log',
    level=logging.INFO,
    format='%(asctime)s %(levelname)s: %(message)s'
)

@app.before_request
def log_all_requests():
    if request.method == 'POST' and request.get_data():
        body = request.get_data(as_text=True)
        app.logger.info(f"POST {request.path} Body: {body}")
    else:
        app.logger.info(f"{request.method} {request.path}")


# ROUTES
@app.route("/")
def index():
    return "Hi there"

@app.route("/flag")
def get_flag():
    authed = request.headers.get("X-Proxy-Authenticated", "false")
    if authed.lower() != "true":
        return jsonify({"error": "Bad boy"}), 403

    return jsonify({"flag": FLAG})


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5000, debug=False)
