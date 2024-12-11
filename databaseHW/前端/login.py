from http.server import BaseHTTPRequestHandler, HTTPServer
import json

DEFAULT_USERNAME = "22336095"
DEFAULT_PASSWORD = "4001234567"

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            # 返回 HTML 页面
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("index.html", "rb") as file:
                self.wfile.write(file.read())
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/login":
            # 处理登录请求
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            credentials = json.loads(post_data)

            username = credentials.get("username")
            password = credentials.get("password")

            # 验证用户名和密码
            if username == DEFAULT_USERNAME and password == DEFAULT_PASSWORD:
                response = {"success": True}
            else:
                response = {"success": False}

            # 返回响应
            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

if __name__ == "__main__":
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print("Server running on http://127.0.0.1:8000")
    httpd.serve_forever()
