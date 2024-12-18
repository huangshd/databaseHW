from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import pg8000
from urllib.parse import urlparse, parse_qs
import pyodbc


DEFAULT_USERNAME = "22336095"
DEFAULT_PASSWORD = "1"

class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
    # 初始化背景图片元组
    background_images = (
        "https://th.bing.com/th/id/R.8d6c7a6bd7d75306dac1b07aaf0af79b?rik=ZTg9PZ3MzoDM1A&riu=http%3a%2f%2fimg3.winshang.com%2fUpload%2fbrand%2f2018%2f6%2f13%2f131733469978942470.png&ehk=%2beSxehMQL9CxUus%2buamOyzcuj5fV9rWG2qlGxW6u9IY%3d&risl=&pid=ImgRaw&r=0&sres=1&sresct=1",
        "https://th.bing.com/th/id/R.10299f3356f5fbc0458fdcedb5b72c55?rik=myv8SuVUWLsVCw&pid=ImgRaw&r=0",
        "https://th.bing.com/th/id/R.08bdb73cf0c518a72c812aa6dfbfb019?rik=O58TZ2%2bTBNF5sA&pid=ImgRaw&r=0",
        "https://th.bing.com/th/id/OIP.Dh1YkayYmXwIAzke8kUy4QHaE8?rs=1&pid=ImgDetMain",
        "https://th.bing.com/th/id/OIP.Xpt_NtPaKjxD4z_FyNb_mgHaHa?rs=1&pid=ImgDetMain",
        "https://th.bing.com/th/id/OIP.GdiXo9jd0Toit8L1XaB72QHaEo?rs=1&pid=ImgDetMain",
        "https://th.bing.com/th/id/OIP.GdiXo9jd0Toit8L1XaB72QHaEo?rs=1&pid=ImgDetMain",
        "https://th.bing.com/th/id/OIP.GdiXo9jd0Toit8L1XaB72QHaEo?rs=1&pid=ImgDetMain",
        "https://th.bing.com/th/id/OIP.GdiXo9jd0Toit8L1XaB72QHaEo?rs=1&pid=ImgDetMain",
        "https://th.bing.com/th/id/OIP.GdiXo9jd0Toit8L1XaB72QHaEo?rs=1&pid=ImgDetMain",
        "https://th.bing.com/th/id/OIP.GdiXo9jd0Toit8L1XaB72QHaEo?rs=1&pid=ImgDetMain",
        "https://th.bing.com/th/id/OIP.GdiXo9jd0Toit8L1XaB72QHaEo?rs=1&pid=ImgDetMain",
        "https://th.bing.com/th/id/OIP.GdiXo9jd0Toit8L1XaB72QHaEo?rs=1&pid=ImgDetMain",
    )

    def do_GET(self):
        parsed_path = urlparse(self.path)
        path = parsed_path.path

        print(f"Received GET request for path: {path}")

        if path == "/":
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            with open("index.html", "rb") as file:
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

        elif path.startswith("/restaurant/"):
            restaurant_id = path.split('/')[-1]
            if restaurant_id.isdigit():
                print(f"Fetching details for restaurant ID: {restaurant_id}")

                # 获取餐厅的详细数据
                restaurant_data = self.get_restaurant_details(restaurant_id)

                if restaurant_data:
                    # 读取模板文件
                    with open("restaurant_detail.html", 'r', encoding='utf-8') as file:
                        template_content = file.read()

                    # 使用数据填充模板
                    html_content = template_content.replace("{{restaurant_name}}", restaurant_data['restaurant_name'])
                    html_content = html_content.replace("{{restaurant_address}}", restaurant_data['restaurant_address'])
                    html_content = html_content.replace("{{restaurant_number}}", restaurant_data['restaurant_number'])
                    html_content = html_content.replace("{{restaurant_description}}",
                                                        restaurant_data['restaurant_description'])
                    html_content = html_content.replace("{{background_image_url}}",
                                                        restaurant_data['background_image_url'])

                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(html_content.encode("utf-8"))
                else:
                    self.send_response(404)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"Restaurant not found")

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

        # 查询餐厅名称和平均评分
        cursor.execute("""
            SELECT r.restrant_id, r.name, r.background_image_url, 
                   AVG(c.rating) AS avg_rating 
            FROM Restaurants r
            LEFT JOIN Comments c ON r.restrant_id = c.rest_id
            GROUP BY r.restrant_id, r.name, r.background_image_url
        """)

        # 生成餐厅名称和评分的 HTML
        html = ""
        image_index = 0  # 用来循环访问背景图片元组

        for row in cursor.fetchall():
            # 获取背景图片 URL（循环使用背景图片元组中的图片）
            background_image_url = self.background_images[image_index]

            # 获取餐厅的平均评分
            avg_rating = row.avg_rating if row.avg_rating is not None else 0

            html += f'''
            <div class="restaurant-item" style="background-image: url('{background_image_url}')">
                <h3>{row.name}</h3>
                <p>Rating: {avg_rating:.1f}</p>
                <a href="/restaurant/{row.restrant_id}">View Details</a>
            </div>
            '''

            # 更新背景图片的索引，确保循环使用
            image_index = (image_index + 1) % len(self.background_images)

        conn.close()
        return html

    def render_restaurant_details(self, details):
        # 使用字符串格式化将餐厅详情数据渲染到 HTML 模板中
        return f'''
        <html>
        <head><title>{details['restaurant_name']} Details</title></head>
        <body>
            <div class="flex-container" style="background-image: url('{details['background_image_url']}');">
                <div class="container">
                    <h1>{details['restaurant_name']}</h1>
                    <p><strong>Address:</strong> {details['restaurant_address']}</p>
                    <p><strong>Phone Number:</strong> {details['restaurant_number']}</p>
                    <p><strong>Description:</strong> {details['restaurant_description']}</p>
                    <a href="/user" class="back-link">Back to User Page</a>
                </div>
            </div>
        </body>
        </html>
        '''

    def get_restaurant_details(self, restaurant_id):
        # 连接数据库并获取餐厅详细信息
        conn = pyodbc.connect(
            r'DRIVER={ODBC Driver 17 for SQL Server};'
            r'SERVER=CHARLESHUANG\FUCKTHAT;'
            r'DATABASE=Restaurants;'
            r'UID=22336095;'
            r'PWD=4001234567'
        )
        cursor = conn.cursor()
        cursor.execute(
            f"SELECT name, address, number, description, background_image_url FROM Restaurants WHERE restrant_id = {restaurant_id}"
        )

        row = cursor.fetchone()
        conn.close()

        if row:
            # 将数据作为字典返回
            return {
                'restaurant_name': row.name,
                'restaurant_address': row.address,
                'restaurant_number': row.number,
                'restaurant_description': row.description,
                'background_image_url': row.background_image_url
            }
        else:
            return None


if __name__ == "__main__":
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print("Server running on http://127.0.0.1:8000")
    httpd.serve_forever()
