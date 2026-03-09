from flask import Flask, render_template_string
import os

app = Flask(__name__)

UPLOAD_BASE = os.environ.get("UPLOAD_BASE", "/app/uploads")


@app.route("/")
def index():
    return """
    <!DOCTYPE html>
    <html>
    <head><title>Admin Panel</title></head>
    <body>
        <h1>Admin Panel</h1>
        <p>Welcome, administrator.</p>
    </body>
    </html>
    """

@app.get('/logs')
def logs():
    with open('/tmp/app.log', 'r') as f:
        log_content = f.read()
    return render_template_string(log_content)

@app.get('/clean')
def clean():
    with open('/tmp/app.log', 'w') as f:
        pass
    return "CLEANED"


if __name__ == "__main__":
    app.run(host="127.0.0.1", port=5001, debug=False)
