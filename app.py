from flask import Flask, request, render_template_string, Response
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
        <pre>{{ response|safe }}</pre>
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
            # Make the request to the specified URL
            resp = requests.get(url)
            resp.raise_for_status()
            # Return the response content to be rendered
            content = resp.text
            return render_template_string(HTML_FORM, response=content, requested_url=url)
        except requests.exceptions.RequestException as e:
            # Return the error message to be rendered
            return render_template_string(HTML_FORM, response=f"An error occurred: {e}", requested_url=url)
    return render_template_string(HTML_FORM, response="Bad Request: URL parameter is missing", requested_url=None)


