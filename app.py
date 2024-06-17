from flask import Flask, request, render_template_string, redirect, url_for
import requests

app = Flask(__name__)

HTML_FORM = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Proxy Server</title>
    <style>
        /* Your CSS styles here */
    </style>
</head>
<body>
    <div class="container">
        <h1>Enter URL to Proxy</h1>
        <form method="post" action="/proxy">
            <input type="text" name="url" placeholder="Enter URL" required>
            <button type="submit">Fetch URL (Through Proxy)</button>
        </form>
        {% if response_proxy %}
            <h2>Response from Proxy: {{ requested_url }}</h2>
            <div>{{ response_proxy|safe }}</div>
        {% endif %}

        <h1>Directly Connect to Other Server</h1>
        <form method="post" action="/switch">
            <input type="text" name="url_direct" placeholder="Enter URL" required>
            <button type="submit">Fetch URL (Directly)</button>
        </form>
        {% if response_direct %}
            <h2>Response from Direct Server: {{ requested_url_direct }}</h2>
            <div>{{ response_direct|safe }}</div>
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
    return redirect(url_for('fetch_url_proxy', url=url))

@app.route('/fetch_proxy', methods=['GET', 'POST'])
def fetch_url_proxy():
    url = request.args.get('url')
    method = request.method
    data = request.form.to_dict() if method == 'POST' else request.args.to_dict()
    
    if url:
        try:
            # Make the request to the specified URL through the proxy
            if method == 'POST':
                resp = requests.post(url, data=data)
            else:
                resp = requests.get(url, params=data)
            
            resp.raise_for_status()
            
            # Process HTML content to rewrite links and forms
            content = resp.text
            base_url = url
            content = content.replace('href="/', f'href="{url_for("fetch_url_proxy", url=base_url)}/')
            content = content.replace('src="/', f'src="{url_for("fetch_url_proxy", url=base_url)}/')
            content = content.replace('action="/', f'action="{url_for("fetch_url_proxy", url=base_url)}?')

            return render_template_string(HTML_FORM, response_proxy=content, requested_url=url)
        except requests.exceptions.RequestException as e:
            return render_template_string(HTML_FORM, response_proxy=f"An error occurred: {e}", requested_url=url)

    return render_template_string(HTML_FORM, response_proxy="Bad Request: URL parameter is missing", requested_url=None)

@app.route('/switch', methods=['POST'])
def switch_server():
    url_direct = request.form.get('url_direct')
    return redirect(url_for('fetch_url_direct', url_direct=url_direct))

@app.route('/fetch_direct', methods=['GET', 'POST'])
def fetch_url_direct():
    url_direct = request.args.get('url_direct')
    
    if url_direct:
        try:
            # Make the request directly to the other server
            resp = requests.get(url_direct)
            resp.raise_for_status()
            content = resp.text
            
            # Optionally process content here if needed
            
            return render_template_string(HTML_FORM, response_direct=content, requested_url_direct=url_direct)
        except requests.exceptions.RequestException as e:
            return render_template_string(HTML_FORM, response_direct=f"An error occurred: {e}", requested_url_direct=url_direct)

    return render_template_string(HTML_FORM, response_direct="Bad Request: URL parameter is missing", requested_url_direct=None)

if __name__ == '__main__':
    app.run(debug=True)
