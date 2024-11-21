from http.server import BaseHTTPRequestHandler, HTTPServer

class RequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.handle_request()

    def do_POST(self):
        self.handle_request()

    def do_PUT(self):
        self.handle_request()

    def do_DELETE(self):
        self.handle_request()

    def handle_request(self):
        # Get the raw HTTP request line and headers
        raw_request = self.requestline + "\n" + str(self.headers)

        # If there's a body, read it
        content_length = int(self.headers.get('Content-Length', 0))
        if content_length > 0:
            raw_request += "\n" + self.rfile.read(content_length).decode('utf-8', errors='backslashreplace')

        # Send response status code
        self.send_response(200)
        self.send_header('Content-type', 'text/plain')
        self.end_headers()

        # Write the raw request to the response
        self.wfile.write(raw_request.encode('utf-8'))

def run(server_class=HTTPServer, handler_class=RequestHandler, port=8080):
    server_address = ('', port)
    httpd = server_class(server_address, handler_class)
    print(f'Serving on port {port}...')
    httpd.serve_forever()

if __name__ == "__main__":
    run()
