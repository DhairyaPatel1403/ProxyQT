import http.server
import socketserver
import requests
import urllib.parse

PORT = 8080

class Proxy(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            # Serve the HTML form
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(b"""
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
                </body>
                </html>
            """)
        else:
            # Forward the request to the actual target
            url = self.path[1:]  # Remove leading '/'
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            
            try:
                response = requests.get(url)
                response.raise_for_status()
                self.wfile.write(response.content)
            except requests.exceptions.RequestException as e:
                self.wfile.write(f"An error occurred: {e}".encode())

    def do_POST(self):
        if self.path == '/proxy':
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length).decode('utf-8')
            parsed_data = urllib.parse.parse_qs(post_data)
            url = parsed_data.get('url', [None])[0]
            
            if url:
                self.send_response(200)
                self.send_header('Content-type', 'text/html')
                self.end_headers()
                
                try:
                    response = requests.get(url)
                    response.raise_for_status()
                    self.wfile.write(response.content)
                except requests.exceptions.RequestException as e:
                    self.wfile.write(f"An error occurred: {e}".encode())
            else:
                self.send_response(400)
                self.end_headers()
                self.wfile.write(b"Bad Request: URL parameter is missing")
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b"Not Found")

# Set up the HTTP server
with socketserver.TCPServer(("", PORT), Proxy) as httpd:
    print(f"Serving at port {PORT}")
    httpd.serve_forever()
