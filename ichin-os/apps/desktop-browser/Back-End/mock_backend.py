from http.server import HTTPServer, BaseHTTPRequestHandler
import json

class MockHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/session':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "workspaces": [
                    {"id": "work", "name": "Work", "color": "#3b82f6", "icon": "briefcase"}
                ],
                "tabs": [
                    {"id": "1", "title": "GitHub", "url": "https://github.com", "favicon": "icon-github", "pinned": True, "workspace_id": "work"}
                ],
                "active_workspace": "work",
                "active_tab": "1"
            }
            self.wfile.write(json.dumps(response).encode())
        else:
            self.send_response(404)
            self.end_headers()

    def log_message(self, format, *args):
        pass  # Suppress log messages

if __name__ == '__main__':
    server = HTTPServer(('127.0.0.1', 3001), MockHandler)
    print('Mock backend running on http://127.0.0.1:3001')
    server.serve_forever()