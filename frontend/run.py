import http.server
import socketserver
import os

PORT = 5000
Handler = http.server.SimpleHTTPRequestHandler

if __name__ == "__main__":
    # Ensure we are in the frontend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    # Allow port reuse
    socketserver.TCPServer.allow_reuse_address = True
    with socketserver.TCPServer(("", PORT), Handler) as httpd:
        print(f"Frontend serving at http://localhost:{PORT}")
        httpd.serve_forever()
