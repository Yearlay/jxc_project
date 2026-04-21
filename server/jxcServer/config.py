import os

# 数据库连接配置
DB_HOST     = os.getenv('DB_HOST',     '192.168.0.116')
DB_PORT     = int(os.getenv('DB_PORT', '5432'))
DB_NAME     = os.getenv('DB_NAME',     'jxc')
DB_USER     = os.getenv('DB_USER',     'onepiece')
DB_PASSWORD = os.getenv('DB_PASSWORD', 'yearlay_1987')

# JWT 密钥（生产环境请通过环境变量注入）
JWT_SECRET  = os.getenv('JWT_SECRET',  'jxc_secret_2026')

# Flask
DEBUG = os.getenv('FLASK_DEBUG', 'true').lower() == 'true'
PORT  = int(os.getenv('PORT', '5001'))
