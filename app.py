import os
import sys
from flask import Flask, jsonify, request
from flask_sqlalchemy import SQLAlchemy  # 导入扩展类
from flask_jwt_extended import JWTManager, create_access_token, jwt_required, get_jwt_identity

app = Flask(__name__)
# 配置数据库连接
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.root_path, 'data.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False  # 关闭对模型修改的监控

# 配置JWT
app.config['JWT_SECRET_KEY'] = 'your_jwt_secret_key'  # 设置JWT的密钥

db = SQLAlchemy(app)  # 初始化扩展，传入程序实例 app
jwt = JWTManager(app)  # 初始化JWT扩展

# 用户模型
class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)  # 存储密码

    def __repr__(self):
        return f'<User {self.username}>'


# 注册用户路由
@app.route('/register', methods=['POST'])
def register():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # 检查用户名是否已存在
    user = User.query.filter_by(username=username).first()
    if user:
        return jsonify({"message": "Username already exists"}), 400

    # 创建新用户
    new_user = User(username=username, password=password)
    db.session.add(new_user)
    db.session.commit()

    return jsonify({"message": "User created successfully"}), 201


# 登录路由，验证用户并生成JWT
@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    # 查询用户
    user = User.query.filter_by(username=username).first()

    # 验证用户凭证
    if user and user.password == password:
        # 生成JWT令牌
        access_token = create_access_token(identity=username)
        return jsonify(access_token=access_token), 200
    else:
        return jsonify({"message": "Invalid credentials"}), 401


# 受保护的路由，只有登录后才能访问
@app.route('/protected', methods=['GET'])
@jwt_required()  # 保护该路由，需要JWT才能访问
def protected():
    current_user = get_jwt_identity()  # 获取当前用户的身份（即用户名）
    return jsonify(logged_in_as=current_user), 200

# 初始化数据库
@app.before_first_request
def create_tables():
    db.create_all()

# 示例路由
@app.route('/')
def index():
    return jsonify({'message': 'Flask is connected to OpenGauss!'})

# 启动服务
if __name__ == '__main__':
    app.run(debug=True)