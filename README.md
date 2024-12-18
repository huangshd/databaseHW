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