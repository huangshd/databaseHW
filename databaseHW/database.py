import psycopg2
from psycopg2 import OperationalError
import pytest

def connect_to_database():
    try:
        # 连接到 OpenGauss 数据库
        connection = psycopg2.connect(
            database = "postgres",
            user = "admin",
            password = "admin@123",
            host = "192.168.27.129",
            port = "7654"
        )
        print("Connected to the database successfully.")
        return connection
    except OperationalError as e:
        print("Error while connecting to OpenGauss:", e)
        pytest.fail(str(e))
        return None



def delete_table(connection, table_name):
    try:
        cursor = connection.cursor()
        # 定义删除表的 SQL 语句
        drop_table_query = f"DROP TABLE IF EXISTS {table_name};"
        cursor.execute(drop_table_query)
        connection.commit()  # 提交事务
        print(f"Table '{table_name}' deleted successfully (if it existed).")
        cursor.close()
    except Exception as e:
        print(f"Error occurred while deleting table '{table_name}':", e)
        pytest.fail(str(e))

def create_table_users(connection):
    try:
        # 创建游标对象
        cursor = connection.cursor()

        # 定义创建表的 SQL 语句
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS users (
            user_id VARCHAR(100) NOT NULL,  
            user_name VARCHAR(100) NOT NULL,
            pass_word VARCHAR(100) NOT NULL,
            email VARCHAR(100) NOT NULL,
            role INT NOT NULL,
            phone_number VARCHAR(100) NOT NULL,           
            PRIMARY KEY(user_id)
        );
        """
        # 执行创建表的 SQL 查询
        cursor.execute(create_table_query)
        connection.commit()  # 提交事务
        print(f"Table users created successfully or already exists.")

        # 关闭游标
        cursor.close()
    except Exception as e:
        print(f"Error occurred while creating table users :", e)
        pytest.fail(str(e))

def create_table_restaurants(connection):
    try:
        # 创建游标对象
        cursor = connection.cursor()

        # 定义创建表的 SQL 语句
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS restaurants (
            rest_id VARCHAR(100) NOT NULL,  
            rest_name VARCHAR(100) NOT NULL,
            address VARCHAR(255) NOT NULL,
            phone_number VARCHAR(100) NOT NULL,
            description VARCHAR(255) NOT NULL,           
            PRIMARY KEY(rest_id)
        );
        """
        # 执行创建表的 SQL 查询
        cursor.execute(create_table_query)
        connection.commit()  # 提交事务
        print(f"Table restaurants created successfully or already exists.")

        # 关闭游标
        cursor.close()
    except Exception as e:
        print(f"Error occurred while creating table restaurants :", e)
        pytest.fail(str(e))

def create_table_dishes(connection):
    try:
        # 创建游标对象
        cursor = connection.cursor()

        # 定义创建表的 SQL 语句
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS dishes (
            dish_id VARCHAR(100) NOT NULL,  
            rest_id VARCHAR(100) NOT NULL,
            dish_name VARCHAR(100) NOT NULL,
            price  INT NOT NULL,
            description VARCHAR(255) NOT NULL,           
            PRIMARY KEY (dish_id),
            FOREIGN KEY (rest_id) REFERENCES restaurants(rest_id)
        );
        """
        # 执行创建表的 SQL 查询
        cursor.execute(create_table_query)
        connection.commit()  # 提交事务
        print(f"Table dishes created successfully or already exists.")

        # 关闭游标
        cursor.close()
    except Exception as e:
        print(f"Error occurred while creating table dishes :", e)
        pytest.fail(str(e))

def create_table_comments(connection):
    try:
        # 创建游标对象
        cursor = connection.cursor()

        # 定义创建表的 SQL 语句
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS comments (
            comment_id VARCHAR(100) NOT NULL,  --该评论的id
            user_id VARCHAR(100) NOT NULL,
            rest_id VARCHAR(100) NOT NULL,
            dish_id  VARCHAR(100) NOT NULL,
            content VARCHAR(255) NOT NULL,
            rating  FLOAT NOT NULL CHECK (rating BETWEEN 1.0 AND 5.0),         
            PRIMARY KEY (comment_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (dish_id) REFERENCES dishes(dish_id),
            FOREIGN KEY (rest_id) REFERENCES restaurants(rest_id)
        );
        """
        # 执行创建表的 SQL 查询
        cursor.execute(create_table_query)
        connection.commit()  # 提交事务
        print(f"Table comments created successfully or already exists.")

        # 关闭游标
        cursor.close()
    except Exception as e:
        print(f"Error occurred while creating table comments :", e)
        pytest.fail(str(e))

def create_table_orders(connection):
    try:
        # 创建游标对象
        cursor = connection.cursor()

        # 定义创建表的 SQL 语句
        create_table_query = f"""
        CREATE TABLE IF NOT EXISTS orders (
            order_id VARCHAR(100) NOT NULL,  
            user_id VARCHAR(100) NOT NULL,
            rest_id VARCHAR(100) NOT NULL,
            total_price INT NOT NULL,
            order_status VARCHAR(100) NOT NULL,  --订单的状态(待支付、已完成)        
            PRIMARY KEY (order_id),
            FOREIGN KEY (user_id) REFERENCES users(user_id),
            FOREIGN KEY (rest_id) REFERENCES restaurants(rest_id)
        );
        """
        # 执行创建表的 SQL 查询
        cursor.execute(create_table_query)
        connection.commit()  # 提交事务
        print(f"Table orders created successfully or already exists.")

        # 关闭游标
        cursor.close()
    except Exception as e:
        print(f"Error occurred while creating table orders :", e)
        pytest.fail(str(e))

def insert_user_data(connection, data):
    try:
        cursor = connection.cursor()
        # 定义插入数据的 SQL 语句(要改，每个表都不一样)
        insert_query = f"INSERT INTO users VALUES (%s, %s, %s, %s, %s, %s);"
        cursor.executemany(insert_query, data)  # 插入多行数据
        connection.commit()  # 提交事务
        print(f"Data inserted successfully into table users.")
        cursor.close()
    except Exception as e:
        print(f"Error occurred while inserting data into table users:", e)
        pytest.fail(str(e))

def insert_restaurant_data(connection, data):
    try:
        cursor = connection.cursor()
        # 定义插入数据的 SQL 语句(要改，每个表都不一样)
        insert_query = f"INSERT INTO restaurants VALUES (%s, %s, %s, %s, %s);"
        cursor.executemany(insert_query, data)  # 插入多行数据
        connection.commit()  # 提交事务
        print(f"Data inserted successfully into table restaurants.")
        cursor.close()
    except Exception as e:
        print(f"Error occurred while inserting data into table restaurants:", e)
        pytest.fail(str(e))

def insert_dish_data(connection, data):
    try:
        cursor = connection.cursor()
        # 定义插入数据的 SQL 语句(要改，每个表都不一样)
        insert_query = f"INSERT INTO dishes VALUES (%s, %s, %s, %s, %s);"
        cursor.executemany(insert_query, data)  # 插入多行数据
        connection.commit()  # 提交事务
        print(f"Data inserted successfully into table dishes.")
        cursor.close()
    except Exception as e:
        print(f"Error occurred while inserting data into table dishes:", e)
        pytest.fail(str(e))

def insert_comment_data(connection, data):
    try:
        cursor = connection.cursor()
        # 定义插入数据的 SQL 语句(要改，每个表都不一样)
        insert_query = f"INSERT INTO comments VALUES (%s, %s, %s, %s, %s, %s);"
        cursor.executemany(insert_query, data)  # 插入多行数据
        connection.commit()  # 提交事务
        print(f"Data inserted successfully into table comments.")
        cursor.close()
    except Exception as e:
        print(f"Error occurred while inserting data into table comments:", e)
        pytest.fail(str(e))

def insert_order_data(connection, data):
    try:
        cursor = connection.cursor()
        # 定义插入数据的 SQL 语句(要改，每个表都不一样)
        insert_query = f"INSERT INTO orders VALUES (%s, %s, %s, %s, %s);"
        cursor.executemany(insert_query, data)  # 插入多行数据
        connection.commit()  # 提交事务
        print(f"Data inserted successfully into table orders.")
        cursor.close()
    except Exception as e:
        print(f"Error occurred while inserting data into table orders:", e)
        pytest.fail(str(e))

# 调用函数
if __name__ == "__main__":
    connection = connect_to_database()
    #若连接成功，则开始建表
    if connection:
        #delete_table(connection, 'orders')
        create_table_users(connection)  # 创建用户表
        create_table_restaurants(connection) # 创建店家表
        create_table_dishes(connection) # 创建菜品表
        create_table_comments(connection) # 创建评价表
        create_table_orders(connection)  # 创建订单表

        #insert_dish_data(connection,[('1','2024','shit',100,'smelly')])
        #insert_comment_data(connection,[('1','2004','2024','1','bad',1)])
        insert_order_data(connection, [('1','2004','2024',499,'done')])

        connection.close()  # 关闭数据库连接