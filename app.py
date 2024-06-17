from flask import Flask, request, render_template_string, redirect, url_for
import requests
from urllib.parse import urlparse


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
    <div class="container">
        <h1>Enter URL to Proxy</h1>
        <form method="post" action="/proxy">
            <input type="text" name="url" placeholder="Enter URL" required>
            <button type="submit">Fetch URL (Main Server)</button>
        </form>
        <form method="post" action="https://proxy-server-1.vercel.app/proxy">
            <input type="text" name="url" placeholder="Enter URL" required>
            <button type="submit">Fetch URL (Proxy Server 1)</button>
        </form>
        {% if response %}
            <h2>Response from {{ requested_url }}</h2>
            <div>{{ response|safe }}</div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET'])
def index():
    return render_template_string(HTML_FORM)

@app.route('/proxy', methods=['POST'])
def proxy():
    url = request.form.get('url')
    return redirect(url_for('fetch_url', url=url))

@app.route('/fetch', methods=['GET', 'POST'])
def fetch_url():
    url = request.args.get('url')
    method = request.method
    data = request.form.to_dict() if method == 'POST' else request.args.to_dict()
    
    if url:
        try:
            # Make the request to the specified URL
            if method == 'POST':
                resp = requests.post(url, data=data)
            else:
                resp = requests.get(url, params=data)
            
            resp.raise_for_status()
            
            # Process HTML content to rewrite links and forms
            content = resp.text
            base_url = urlparse(url)._replace(path='').geturl()
            content = content.replace('href="/', f'href="{url_for("fetch_url", url=base_url)}/')
            content = content.replace('src="/', f'src="{url_for("fetch_url", url=base_url)}/')
            content = content.replace('action="/', f'action="{url_for("fetch_url", url=base_url)}?')

            return render_template_string(HTML_FORM, response=content, requested_url=url)
        except requests.exceptions.RequestException as e:
            return render_template_string(HTML_FORM, response=f"An error occurred: {e}", requested_url=url)

    return render_template_string(HTML_FORM, response="Bad Request: URL parameter is missing", requested_url=None)

