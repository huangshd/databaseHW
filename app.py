import os
from flask import Flask, jsonify, request, render_template, session, flash, redirect, url_for
from flask_jwt_extended import JWTManager, create_access_token
import database as db

app = Flask(__name__)
app.secret_key = 'super_secret_key'  # 用于会话管理和消息提示
jwt = JWTManager(app)  # 初始化JWT扩展
# 提供前端页面
@app.route('/')
def index():
    return render_template('index.html')  # 渲染位于 templates/index.html 的页面

# 登录页面的路由
@app.route('/login', methods=['POST'])
def login():
    # 获取 JSON 请求体
    data = request.get_json()
    user_name = data.get('username')  # 从请求中获取用户名
    password = data.get('password')  # 从请求中获取密码

    print(f"用户尝试登录: {user_name}")

    # 连接数据库并验证用户
    with db.connect_to_database() as connection:
        user_id = db.validate_user(connection, user_name, password)

    if user_id:
        session['user_id'] = user_id  # 将 user_id 存入会话
        session['user_name'] = user_name  # 将 user_name 存入会话
        flash("登录成功！", "success")
        print(f"用户 '{user_name}' 登录成功，用户ID: {user_id}")
        return jsonify(success=True, message="登录成功！", token=create_access_token(identity=user_name))  # 返回成功信息和 JWT
    else:
        flash('用户名或密码错误，登录失败！', 'error')
        print(f"用户 '{user_name}' 登录失败：用户名或密码错误。")
        return jsonify(success=False, message="用户名或密码错误！"), 401  # 返回失败信息

@app.route('/admin')
def admin():
    """返回管理员页面"""
    return render_template('admin.html')

def generate_table(headers, rows):
    """
    生成 HTML 表格
    :param headers: 表头列表
    :param rows: 数据行列表
    :return: HTML 格式的表格
    """
    html = '<table>'
    html += '<thead><tr>'
    for header in headers:
        html += f'<th>{header}</th>'
    html += '</tr></thead>'
    html += '<tbody>'
    for row in rows:
        html += '<tr>'
        for cell in row:
            html += f'<td>{cell}</td>'
        html += '</tr>'
    html += '</tbody>'
    html += '</table>'
    return html

@app.route('/user-table', methods=['GET'])
def user_table():
    """查询用户表并返回 HTML 表格"""
    with db.connect_to_database() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT user_id, user_name, pass_word, email, role, phone_number FROM users;")
        rows = cursor.fetchall()
        headers = [desc[0] for desc in cursor.description]
        cursor.close()

    return generate_table(headers, rows)

@app.route('/merchant-table', methods=['GET'])
def merchant_table():
    """查询商家表并返回 HTML 表格"""
    with db.connect_to_database() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT rest_id, rest_name, address, phone_number, description FROM restaurants;")
        rows = cursor.fetchall()
        headers = [desc[0] for desc in cursor.description]
        cursor.close()

    return generate_table(headers, rows)

@app.route('/dish-table', methods=['GET'])
def dish_table():
    """查询菜品表并返回 HTML 表格"""
    with db.connect_to_database() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT dish_id, rest_id, dish_name, price, description FROM dishes;")
        rows = cursor.fetchall()
        headers = [desc[0] for desc in cursor.description]
        cursor.close()

    return generate_table(headers, rows)

@app.route('/review-table', methods=['GET'])
def review_table():
    """查询评价表并返回 HTML 表格"""
    with db.connect_to_database() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT comment_id, user_id, rest_id, dish_id, content, rating FROM comments;")
        rows = cursor.fetchall()
        headers = [desc[0] for desc in cursor.description]
        cursor.close()

    return generate_table(headers, rows)

@app.route('/order-table', methods=['GET'])
def order_table():
    """查询订单表并返回 HTML 表格"""
    with db.connect_to_database() as connection:
        cursor = connection.cursor()
        cursor.execute("SELECT order_id, user_id, rest_id, total_price, order_status FROM orders;")
        rows = cursor.fetchall()
        headers = [desc[0] for desc in cursor.description]
        cursor.close()

    return generate_table(headers, rows)


if __name__ == '__main__':
    # 让 Flask 监听 8000 端口
    app.run(host='127.0.0.1', port=8000, debug=True)
