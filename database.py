import pymysql
import os
from dotenv import load_dotenv
from typing import List, Dict, Optional

load_dotenv()

class Database:
    def __init__(self):
        self.conn = pymysql.connect(
            host=os.getenv('DB_HOST'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD'),
            port=int(os.getenv('DB_PORT', 3306)),  # Default MySQL port is 3306
            db=os.getenv('DB_NAME'),
            cursorclass=pymysql.cursors.DictCursor
        )
    
    def execute_query(self, query: str, args: Optional[tuple] = None) -> List[Dict]:
        with self.conn.cursor() as cursor:
            cursor.execute(query, args or ())
            result = cursor.fetchall()
            self.conn.commit()
            return result
    
    def close(self):
        self.conn.close()