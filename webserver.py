from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os

g_rpc = None

class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        data = None
        mimetype = "text/html"
        if self.path.endswith(".js"):
            mimetype = "application/javascript"
        if self.path in ["/exploit.js", "/index.html"]:
            with open(os.path.join("exploit", self.path[1:]), "r") as fin:
                data = fin.read()
        elif self.path == "/":
            data = "<a href='/index.html'>exploit</a>"
        elif self.path == "/rop.js":
            data = g_rpc.initial_chain().generate_js()

        if data:
            self.send_response(200)
            self.send_header('Content-type', mimetype)
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_response(404)


def webserver(host, port, rpc):
    global g_rpc
    g_rpc = rpc

    server = HTTPServer((host, port), RequestHandler)
    server.serve_forever()
