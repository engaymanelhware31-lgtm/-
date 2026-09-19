from http.server import ThreadingHTTPServer, SimpleHTTPRequestHandler
from pathlib import Path
import json, threading

ROOT = Path(__file__).resolve().parent
DATA = ROOT / 'data.json'
LOCK = threading.Lock()
DEFAULT = {"customers":[],"receipts":[],"payments":[],"employees":[],"salaries":[],"companyName":"","projects":[],"quotes":[]}

if not DATA.exists():
    DATA.write_text(json.dumps(DEFAULT, ensure_ascii=False, indent=2), encoding='utf-8')

def read_db():
    try:
        return json.loads(DATA.read_text(encoding='utf-8'))
    except Exception:
        return DEFAULT.copy()

def write_db(db):
    tmp = DATA.with_suffix('.tmp')
    tmp.write_text(json.dumps(db, ensure_ascii=False, indent=2), encoding='utf-8')
    tmp.replace(DATA)

class Handler(SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/api/db':
            with LOCK:
                db = read_db()
            body = json.dumps({"database": db}, ensure_ascii=False).encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type','application/json; charset=utf-8')
            self.send_header('Content-Length',str(len(body)))
            self.end_headers(); self.wfile.write(body); return
        return super().do_GET()

    def do_POST(self):
        if self.path == '/api/db':
            try:
                n = int(self.headers.get('Content-Length','0'))
                db = json.loads(self.rfile.read(n).decode('utf-8'))
                if not isinstance(db, dict): raise ValueError('invalid database')
                with LOCK: write_db(db)
                body = b'{"ok":true}'
                self.send_response(200)
                self.send_header('Content-Type','application/json')
                self.send_header('Content-Length',str(len(body)))
                self.end_headers(); self.wfile.write(body)
            except Exception as e:
                body = json.dumps({"ok":False,"error":str(e)}).encode()
                self.send_response(400)
                self.send_header('Content-Type','application/json')
                self.send_header('Content-Length',str(len(body)))
                self.end_headers(); self.wfile.write(body)
            return
        self.send_error(404)

    def log_message(self, fmt, *args):
        print(fmt % args)

print('محاسبه - الخادم المحلي')
print('افتح من جهاز المدير: http://localhost:8080')
print('ومن أجهزة الموظفين: http://IP-جهاز-المدير:8080')
ThreadingHTTPServer(('0.0.0.0',8080), Handler).serve_forever()
