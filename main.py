import json
from http.server import HTTPServer, BaseHTTPRequestHandler
import urllib.parse
from pathlib import Path
import mimetypes
import socket
from time import sleep
import threading
from datetime import datetime


class HttpHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        pr_url = urllib.parse.urlparse(self.path)
        if pr_url.path == '/':
            self.send_html_file('index.html')
        elif pr_url.path == '/message.html':
            self.send_html_file('message.html')
        else:
            file = BASE_DIR.joinpath(pr_url.path[1:])
            if file.exists():
                self.send_static(file)
            else:
                self.send_html_file('error.html', 404)

    def do_POST(self):
        size = self.headers.get('Content-Length')
        data = self.rfile.read(int(size))
        parse_data = urllib.parse.unquote_plus(data.decode())

        client = threading.Thread(target=simple_client, args=(HOST, PORT, parse_data))
        client.start()

        self.send_response(302)
        self.send_header('Location', '/message.html')
        self.end_headers()

    def send_html_file(self, filename, status=200):
        self.send_response(status)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())

    def send_static(self, filename, status=200):
        self.send_response(status)
        mime_type, *_ = mimetypes.guess_type(filename)
        if mime_type:
            self.send_header('Content-type', mime_type)
        else:
            self.send_header('Content-type', 'rext/plain')
        self.end_headers()
        with open(filename, 'rb') as fd:
            self.wfile.write(fd.read())


def run_http_server(server_class=HTTPServer, handler_class=HttpHandler):
    server_address = ('localhost', 3000)
    http = server_class(server_address, handler_class)
    try:
        http.serve_forever()
    except KeyboardInterrupt:
        http.server_close()


def echo_server(host, port):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind((host, port))

        while True:
            data, addr = s.recvfrom(1024)
            print(f"Connected by {addr}")
            server_thread = threading.Thread(target=handle_client, args=(data, addr))
            server_thread.start()


def handle_client(data, addr):
    parse_data_split = data.decode('utf-8').split('&')

    parse_dict = {}
    for el in parse_data_split:
        dict_el = el.split('=')
        parse_dict[dict_el[0]] = dict_el[1]
    with open('storage/data.json', 'r', encoding='utf-8') as fr:
        db = fr.read()
    db_json = json.loads(db)
    db_json[str(datetime.now())] = parse_dict
    with open('storage/data.json', 'w', encoding='utf-8') as fw:
        json.dump(db_json, fw, ensure_ascii=False, indent=4)


def simple_client(host, port, data):
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        while True:
            try:
                s.connect((host, port))
                s.sendall(bytes(data, 'utf-8'))
                break
            except ConnectionRefusedError:
                sleep(0.5)


BASE_DIR = Path()
HOST = '127.0.0.1'
PORT = 5000

if __name__ == '__main__':

    http_server = threading.Thread(target=run_http_server)
    server = threading.Thread(target=echo_server, args=(HOST, PORT))

    http_server.start()
    server.start()
    http_server.join()
    server.join()
