from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import pg8000
from urllib.parse import urlparse, parse_qs
import pyodbc

DEFAULT_USERNAME = "22336095"
DEFAULT_PASSWORD = "1"

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        if self.path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("index.html", "rb") as file:  # 确保 index.html 存在
                self.wfile.write(file.read())

        elif path == "/user":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()

            # 获取餐厅名称
            restaurant_names_html = self.get_restaurant_names()

            # 渲染 user.html 页面并在适当位置插入餐厅名称
            with open("user.html", 'r', encoding='utf-8') as file:
                html_content = file.read()

            # 将餐厅名称插入到页面中
            html_content = html_content.replace("{{restaurant_names}}", restaurant_names_html)

            self.wfile.write(html_content.encode("utf-8"))
        elif path == "/admin":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("admin.html", "rb") as file:
                self.wfile.write(file.read())
        else:
            self.send_response(404)
            self.end_headers()

    def get_restaurant_names(self):
        # 连接到 SQL Server 数据库
        conn = pyodbc.connect(
            r'DRIVER={ODBC Driver 17 for SQL Server};'
            r'SERVER=CHARLESHUANG\FUCKTHAT;'  # 使用您的 SQL Server 实例名称
            r'DATABASE=Restaurants;'  # 使用数据库名称
            r'UID=22336095;'  # 输入您的 SQL Server 用户名
            r'PWD=4001234567'  # 输入您的 SQL Server 密码
        )

        cursor = conn.cursor()

        # 查询餐厅名称
        cursor.execute("SELECT name FROM restaurant")

        # 生成餐厅名称的 HTML
        html = "<ul>"
        for row in cursor.fetchall():
            html += f"<li>{row.name}</li>"  # row.name 是餐厅名称
        html += "</ul>"

        conn.close()
        return html

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
        conn = pg8000.connect(
            database="postgres",
            user="admin",
            password="admin@123",
            host="192.168.27.129",
            port=7654
        )
        cursor = conn.cursor()
        cursor.execute(f"SELECT * FROM {table_name}")
        rows = cursor.fetchall()
        columns = [desc[0] for desc in cursor.description]
        conn.close()

        html = "<table><tr>"
        for column in columns:
            html += f"<th>{column}</th>"
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
