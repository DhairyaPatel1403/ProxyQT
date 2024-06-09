from flask import Flask, request, render_template_string
import requests

app = Flask(__name__)

HTML_FORM = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Proxy Server</title>
</head>
<body>
    <h1>Enter URL to Proxy</h1>
    <form method="post" action="/proxy">
        <input type="text" name="url" placeholder="Enter URL" required>
        <button type="submit">Fetch URL</button>
    </form>
    {% if response %}
        <h2>Response from {{ requested_url }}</h2>
        <pre>{{ response }}</pre>
    {% endif %}
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_FORM)

@app.route('/proxy', methods=['POST'])
def proxy():
    url = request.form.get('url')
    if url:
        try:
            response = requests.get(url)
            response.raise_for_status()
            content = response.text
        except requests.exceptions.RequestException as e:
            content = f"An error occurred: {e}"
        return render_template_string(HTML_FORM, response=content, requested_url=url)
    return render_template_string(HTML_FORM, response="Bad Request: URL parameter is missing", requested_url=None)

