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