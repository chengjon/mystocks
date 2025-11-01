import mysql.connector
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

def check_mysql_tables():
    try:
        # 从环境变量获取数据库配置
        host = os.getenv('MYSQL_HOST', 'localhost')
        user = os.getenv('MYSQL_USER', 'root')
        password = os.getenv('MYSQL_PASSWORD', '')
        port = int(os.getenv('MYSQL_PORT', '3306'))
        database = os.getenv('MYSQL_DATABASE', 'quant_research')

        # 连接到MySQL数据库
        conn = mysql.connector.connect(
            host=host,
            user=user,
            password=password,
            port=port,
            database=database
        )
        
        cursor = conn.cursor()
        
        # 显示所有表
        cursor.execute('SHOW TABLES')
        tables = cursor.fetchall()
        print('MySQL mystocks数据库中的表:')
        for table in tables:
            print(f'  - {table[0]}')
            
        # 显示tick_data表结构
        if any(table[0] == 'tick_data' for table in tables):
            cursor.execute('DESCRIBE tick_data')
            print('\ntick_data表结构:')
            columns = cursor.fetchall()
            for column in columns:
                print(f'  {column}')
        
        cursor.close()
        conn.close()
        
    except Exception as e:
        print(f'检查MySQL表时出错: {e}')

if __name__ == '__main__':
    check_mysql_tables()