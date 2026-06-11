import json, os, sys, threading
from http.server import HTTPServer, SimpleHTTPRequestHandler
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from core import monitor

PORT = 9091
FRONTEND_DIR = Path(__file__).resolve().parent / 'frontend'

class NetGuardHandler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self._serve_file('index.html')
        elif self.path.startswith('/css/') or self.path.startswith('/js/'):
            self._serve_file(self.path.lstrip('/'))
        elif self.path == '/api/status':
            self._json(monitor.get_status())
        elif self.path == '/api/devices':
            self._json(monitor.get_devices())
        elif self.path == '/api/alerts':
            self._json(monitor.get_alerts(20))
        elif self.path == '/api/network-history':
            self._json(monitor.get_network_history(6))
        elif self.path == '/api/bandwidth':
            self._json(monitor.get_bandwidth_history())
        else:
            self.send_response(404)
            self.end_headers()
            self.wfile.write(b'{"error":"not found"}')

    def do_POST(self):
        if self.path == '/api/ack-alert':
            try:
                content = self.rfile.read(int(self.headers.get('Content-Length', 0)))
                data = json.loads(content)
                alert_id = data.get('id')
                from core.database import _get_conn
                _get_conn().execute("UPDATE alerts SET acknowledged=1 WHERE id=?", (alert_id,))
                _get_conn().commit()
                self._json({'success': True})
            except Exception as e:
                self._json({'error': str(e)}, 400)
        else:
            self._json({'error':'not found'}, 404)

    def _serve_file(self, name):
        fp = FRONTEND_DIR / name
        if not fp.exists() or not fp.is_file():
            self.send_response(404)
            self.end_headers()
            return
        ext = fp.suffix.lower()
        types = {'.css':'text/css','.js':'application/javascript','.html':'text/html; charset=utf-8','.png':'image/png','.svg':'image/svg+xml'}
        self.send_response(200)
        self.send_header('Content-Type', types.get(ext, 'application/octet-stream'))
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        with open(fp, 'rb') as f:
            self.wfile.write(f.read())

    def _json(self, data, status=200):
        self.send_response(status)
        self.send_header('Content-Type', 'application/json')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()
        self.wfile.write(json.dumps(data, ensure_ascii=False, default=str).encode())

    def log_message(self, format, *args):
        pass

def start_server():
    monitor.start()
    server = HTTPServer(('0.0.0.0', PORT), NetGuardHandler)
    print(f'[NetGuard] Monitor running on http://localhost:{PORT}')
    server.serve_forever()

if __name__ == '__main__':
    start_server()
