12/18 21:23更新
实现了点击每个菜品的评论界面可以显示菜品的评论，主要实现在函数`get_comments_for_dish`中：
```python
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
```
它读取了菜品名称，餐厅id(用于返回上一级)，用户名称以及他们发表的评论。它返回一个包含菜品名称，餐厅id和评论(已经包括了发表评论的人的名字)的字典：
```python
return {
                'dish_name': dish_data.dish_name,
                'restaurant_id': dish_data.restaurant_id,  # 添加餐厅 ID
                'comments': [{'user_name': comment.user_name, 'content': comment.content} for comment in comments]
            }
```
与前面一样，我们在`do_Get`函数中将数据填充进模板即可：
```python
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
```
模板的主体是一个框，框内展示了所有评论，在底部提供一个按钮返回到餐厅的详情列表中：
```python
<body>
    <div class="container">
        <h1>评论: {{dish_name}}</h1>
        <div class="comments-list">
            {{comments}}
        </div>
        <a href="/restaurant/{{restaurant_id}}" class="back-link">返回餐厅介绍</a>
    </div>
</body>
```

12/18 20:24更新  
实现了介绍每个餐厅中的每个菜品的功能，主要实现的位置：
在`login.py`中的`get_restaurant_details`中，我们读取数据库中的菜品的信息并且通过变量`dishes`加入到返回的字典中返回
```python
# 获取菜品信息
        cursor.execute(f"SELECT dish_name, price, description FROM Dishes WHERE rest_id = {restaurant_id}")
        dishes = cursor.fetchall()
```
在`do_GET`函数中，我们渲染了对应的显示菜品的块,然后将它取代掉我们先前定义在`restaurant_detail.html`文件中的占位符
```python
dishes_html = ""
                    for dish in restaurant_data['dishes']:
                        dishes_html += f'''
                            <div class="dish-item">
                                <h3>{dish.dish_name}</h3>
                                <p><strong>价格：</strong> ${dish.price}</p>
                                <p><strong>介绍：</strong> {dish.description}</p>
                            </div>
                        '''

                    html_content = html_content.replace("{{dishes}}", dishes_html)
```
在`restaurant_detail.html`中，我们开多了一个块以供菜品使用
```python
<div class="dishes">
            {{dishes}}
        </div>
```
同时，我们调整了页面的大小，使其自动适应整个页面的块的数量，避免有信息被挤出页面丢失
```python
.flex-container {
            display: flex;
            justify-content: center;  /* 水平居中 */
            align-items: center;      /* 垂直居中 */
            flex-direction:column;
            min-height: 100%;   /* 自适应高度 */
            background-image: url('{{background_image_url}}');
            background-size: cover;  /* 背景图片覆盖整个容器 */
            background-position: center; /* 背景图片居中 */
        }
```

12/18 18:52更新  
实现了将评分显示到餐厅界面中的功能，主要的实现逻辑是在`get_restaurant_names`函数的
````python
cursor.execute("""
            SELECT r.restrant_id, r.name, r.background_image_url, 
                   AVG(c.rating) AS avg_rating 
            FROM Restaurants r
            LEFT JOIN Comments c ON r.restrant_id = c.rest_id
            GROUP BY r.restrant_id, r.name, r.background_image_url
        """)
以及
# 获取餐厅的平均评分
            avg_rating = row.avg_rating if row.avg_rating is not None else 0
````
中实现。在索引搜索函数名就可以找到。在生成html的部分中加入了评分机制(下面代码的第4行)就可以了
```python
html += f'''
            <div class="restaurant-item" style="background-image: url('{background_image_url}')">
                <h3>{row.name}</h3>
                <p>Rating: {avg_rating:.1f}</p>
                <a href="/restaurant/{row.restrant_id}">View Details</a>
            </div>
            '''
```

12/18 18:01更新    
实现了选中`user`界面后可以查看饭店的信息（根据迪哥给的E-R图做的，在这里要注意，我们还需要给饭店表添加一个属性用来存储背景图片的Url否则会无法贴上图片）  
主要的关键函数有`login.py`中的`get_restaurant_names`，它连接数据库之后获取餐厅的名字和背景图片然后根据`user.html`中的模板生成超链接  
`get_restaurant_details`查询了数据库并且把信息返回进来，然后在`login.py`的`59-89`行实现了将读取的数据填充到模板，也就是`restaurant_detail.html`文件  
`login.py`前面的那一堆url元组是用来填充`user`界面的，那个时候没有建好数据库所以直接排列组合了，后面可以再修改或者不改也没有影响

12/18 15:12更新  
注意`login.py`中`48-56`行的代码实现了连接数据库  
```python
conn = pyodbc.connect(
            r'DRIVER={ODBC Driver 17 for SQL Server};'
            r'SERVER=CHARLESHUANG\FUCKTHAT;'  # 使用您的 SQL Server 实例名称
            r'DATABASE=Restaurants;'  # 使用数据库名称
            r'UID=22336095;'  # 输入您的 SQL Server 用户名
            r'PWD=4001234567'  # 输入您的 SQL Server 密码
        )
```
这里需要将自己的DRIVER修改（我们的应该都是一样的），SQL实例名称可以点击最上面的属性找到，其实就是你一开始登录的那个东西  
创建数据库：
```sql
CREATE DATABASE Restaurants;
```
后面自己建表就可以了  
最容易出错的在于用户名和密码，可以通过语句
```sql
USE Restaurants;
GO
EXEC sp_helpuser;
```
来查询当前有权限的用户然后填到上面的UID就可以了，如果想要使用自己的用户名可以通过类似
```sql
USE Restaurants;
GO
CREATE USER [22336095] FOR LOGIN [22336095];
GO

-- 为该用户授予权限
ALTER ROLE db_owner ADD MEMBER [22336095];
GO
```
的语句来实现