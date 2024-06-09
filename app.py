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
        <pre>{{ response }}</pre>
    {% endif %}
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_FORM)

@app.route('/proxy', methods=['GET', 'POST'])
def proxy():
    if request.method == 'POST':
        url = request.form.get('url')
        if url:
            try:
                # Make the request to the specified URL
                resp = requests.get(url)
                # Return the response content and headers
                return Response(resp.content, headers=dict(resp.headers))
            except Exception as e:
                return f"An error occurred: {e}"
        else:
            return "Please provide a URL to proxy."
    return '''
        <form method="post">
            Enter URL to Proxy: <input type="text" name="url">
            <input type="submit" value="Proxy">
        </form>
    '''