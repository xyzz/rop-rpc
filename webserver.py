from BaseHTTPServer import BaseHTTPRequestHandler, HTTPServer
import os
import sys
from config import target

g_rpc = None

class RequestHandler(BaseHTTPRequestHandler):

    def do_GET(self):
        data = None
        mimetype = "text/html"
        if self.path.endswith(".js"):
            mimetype = "application/javascript"
        if self.path in ["/exploit.js", "/index.html"]:
            if self.path == "/exploit.js":
                if '100' in target:
                    self.path = "/exploit_100.js"
                else:
                    self.path = "/exploit_200.js"

            with open(os.path.join("exploit", self.path[1:]), "r") as fin:
                data = fin.read()

        elif self.path == "/":
            data = '''
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Transitional//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-transitional.dtd">
<html>
    
<head>
        <title>HTML Page</title>
</head>

<body bgcolor="#FFFFFF">
This is test.html page
</body>
    
</html>
'''
            data = "<a href='/index.html'>exploit</a>"
        elif self.path == "/rop.js":
            data = g_rpc.initial_chain().generate_js()

        if data:
            self.send_response(200)
            self.send_header('Content-type', mimetype)
            if '100' in target:
                self.send_header('X-Organization', 'Nintendo')
            self.end_headers()
            self.wfile.write(data)
        else:
            self.send_response(404)


def webserver(host, port, rpc):
    global g_rpc
    g_rpc = rpc

    server = HTTPServer((host, port), RequestHandler)
    server.serve_forever()
