from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import psycopg2

DEFAULT_USERNAME = "22336095"
DEFAULT_PASSWORD = "1"

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("index.html", "rb") as file:
                self.wfile.write(file.read())
        elif self.path == "/user":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("user.html", "rb") as file:
                self.wfile.write(file.read())
        elif self.path == "/admin":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("admin.html", "rb") as file:
                self.wfile.write(file.read())
        elif self.path in ["/user-table", "/merchant-table", "/dish-table", "/review-table", "/order-table"]:
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            table_name = self.path[1:].replace("-table", "")
            self.wfile.write(self.generate_table_html(table_name).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        if self.path == "/login":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            credentials = json.loads(post_data)

            username = credentials.get("username")
            password = credentials.get("password")

            if username == DEFAULT_USERNAME and password == DEFAULT_PASSWORD:
                response = {"success": True}
            else:
                response = {"success": False}

            self.send_response(200)
            self.send_header("Content-type", "application/json")
            self.end_headers()
            self.wfile.write(json.dumps(response).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def generate_table_html(self, table_name):
        conn = psycopg2.connect(
            dbname="postgres",
            user="admin",
            password="admin@123",
            host="192.168.27.129",
            port="7654"
        )
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        conn.close()

        html = f"<table><tr>"

        for column in cursor.description:
            html += f"<th>{column[0]}</th>"
        html += "</tr>"

        for row in rows:
            html += "<tr>"
            for cell in row:
                html += f"<td>{cell}</td>"
            html += "</tr>"

        html += "</table>"
        return html

if __name__ == "__main__":
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print("Server running on http://127.0.0.1:8000")
    httpd.serve_forever()