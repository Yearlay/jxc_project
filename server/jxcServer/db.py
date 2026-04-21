import psycopg2
import psycopg2.extras
import config


def get_conn():
    """获取数据库连接"""
    return psycopg2.connect(
        host=config.DB_HOST,
        port=config.DB_PORT,
        dbname=config.DB_NAME,
        user=config.DB_USER,
        password=config.DB_PASSWORD,
        cursor_factory=psycopg2.extras.RealDictCursor,
    )
