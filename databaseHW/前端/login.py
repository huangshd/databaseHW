from http.server import BaseHTTPRequestHandler, HTTPServer
import json
import pg8000
from urllib.parse import urlparse, parse_qs
import pyodbc


# DEFAULT_USERNAME = "22336095"
# DEFAULT_PASSWORD = "1"

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
                # print(restaurant_data)

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

                    # 渲染菜品信息
                    dishes_html = ""
                    for dish in restaurant_data['dishes']:
                        dishes_html += f'''
                            <div class="dish-item">
                                <h3>{dish.dish_name}</h3>
                                <p><strong>价格：</strong> ${dish.price}</p>
                                <p><strong>介绍：</strong> {dish.description}</p>
                                <a href="/comments/{dish.dish_id}" class="comment-button">查看评论</a>    
                            </div>
                        '''
                        # print(dish.dish_id)

                    html_content = html_content.replace("{{dishes}}", dishes_html)

                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(html_content.encode("utf-8"))
                else:
                    self.send_response(404)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"Restaurant not found")



        elif path.startswith("/comments/"):
            dish_id = path.split('/')[-1]
            print(dish_id)
            if dish_id.isdigit():
                print(f"Fetching comments for dish ID: {dish_id}")
                # 获取评论数据
                comments_data = self.get_comments_for_dish(dish_id)
                if comments_data:
                    # 渲染评论页面
                    with open("comments.html", 'r', encoding='utf-8') as file:
                        comments_template = file.read()
                    # 使用数据填充评论模板
                    dish_name = comments_data['dish_name']
                    rest_id = comments_data['restaurant_id']
                    comments_html = ""
                    for comment in comments_data['comments']:
                        comments_html += f'''
                                        <div class="comment-item">
                                            <p><strong>{comment['user_name']}:</strong> {comment['content']}</p>
                                        </div>
                                    '''
                    comments_template = comments_template.replace("{{dish_name}}", dish_name)
                    comments_template = comments_template.replace("{{comments}}", comments_html)
                    comments_template = comments_template.replace("{{restaurant_id}}", str(rest_id))

                    self.send_response(200)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(comments_template.encode("utf-8"))
                else:
                    self.send_response(404)
                    self.send_header("Content-type", "text/html")
                    self.end_headers()
                    self.wfile.write(b"Comments not found")
            else:
                self.send_response(400)
                self.send_header("Content-type", "text/html")
                self.end_headers()
                self.wfile.write(b"Invalid dish ID")

    def do_POST(self):
        if self.path == "/login":
            content_length = int(self.headers['Content-Length'])
            post_data = self.rfile.read(content_length)
            credentials = json.loads(post_data)

            username = credentials.get("username")
            password = credentials.get("password")

            # 使用数据库连接进行验证
            if self.validate_user_credentials(username, password):
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

    def validate_user_credentials(self, username, password):
        # 连接到 SQL Server 数据库
        conn = pyodbc.connect(
            r'DRIVER={ODBC Driver 17 for SQL Server};'
            r'SERVER=CHARLESHUANG\FUCKTHAT;'  # 使用您的 SQL Server 实例名称
            r'DATABASE=Restaurants;'  # 使用数据库名称
            r'UID=22336095;'  # 输入您的 SQL Server 用户名
            r'PWD=4001234567'  # 输入您的 SQL Server 密码
        )

        cursor = conn.cursor()

        # 查询用户表，验证用户名和密码
        cursor.execute("""
            SELECT * FROM Users WHERE user_name = ? AND pass_word = ?
        """, username, password)
        user = cursor.fetchone()
        conn.close()
        if user:
            # 如果找到了匹配的用户，返回 True
            return True
        else:
            # 如果没有找到匹配的用户，返回 False
            return False

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
                <p>评分： {avg_rating:.1f}</p>
                <a href="/restaurant/{row.restrant_id}">View Details</a>
            </div>
            '''

            # 更新背景图片的索引，确保循环使用
            image_index = (image_index + 1) % len(self.background_images)

        conn.close()
        return html

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

        # 获取菜品信息
        cursor.execute(f"SELECT dish_id, dish_name, price, description FROM Dishes WHERE rest_id = {restaurant_id}")
        dishes = cursor.fetchall()
        # print(dishes)

        conn.close()

        if row:
            # 将餐厅信息和菜品信息一起返回
            return {
                'restaurant_name': row.name,
                'restaurant_address': row.address,
                'restaurant_number': row.number,
                'restaurant_description': row.description,
                'background_image_url': row.background_image_url,
                'dishes': dishes  # 添加菜品信息
            }
        else:
            return None

    def get_comments_for_dish(self, dish_id):
        # 连接到 SQL Server 数据库
        conn = pyodbc.connect(
            r'DRIVER={ODBC Driver 17 for SQL Server};'
            r'SERVER=CHARLESHUANG\FUCKTHAT;'  # 使用您的 SQL Server 实例名称
            r'DATABASE=Restaurants;'  # 使用数据库名称
            r'UID=22336095;'  # 输入您的 SQL Server 用户名
            r'PWD=4001234567'  # 输入您的 SQL Server 密码
        )

        cursor = conn.cursor()

        # 获取菜品信息以及关联的餐厅 ID
        cursor.execute(f"""
            SELECT d.dish_name, r.restrant_id AS restaurant_id
            FROM Dishes d
            JOIN Restaurants r ON d.rest_id = r.restrant_id
            WHERE d.dish_id = ?
        """, dish_id)

        dish_data = cursor.fetchone()

        if dish_data:
            # 获取评论数据
            cursor.execute(f"""
                SELECT u.user_name, c.content
                FROM Comments c
                JOIN Users u ON c.user_id = u.user_id
                WHERE c.dish_id = ?
            """, dish_id)

            comments = cursor.fetchall()

            conn.close()

            # 返回数据，包括菜品名称、餐厅 ID 和评论
            return {
                'dish_name': dish_data.dish_name,
                'restaurant_id': dish_data.restaurant_id,  # 添加餐厅 ID
                'comments': [{'user_name': comment.user_name, 'content': comment.content} for comment in comments]
            }
        else:
            conn.close()
            return None


if __name__ == "__main__":
    server_address = ('', 8000)
    httpd = HTTPServer(server_address, SimpleHTTPRequestHandler)
    print("Server running on http://127.0.0.1:8000")
    httpd.serve_forever()
