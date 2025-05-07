from flask import Flask, request, jsonify
from flask_cors import CORS
from database import Database
import os

app = Flask(__name__)
CORS(app, origins=["http://localhost:8080"])  # 限制为前端域名

# 获取数据 API
@app.route('/api/data', methods=['GET'])
def get_data():
    db = Database()
    try:
        # 获取查询参数（如：/api/data?name=刘展鹏）
        search_name = request.args.get('name')
        
        # 基础SQL
        base_sql = "SELECT * FROM Sheet1"
        
        # 动态添加WHERE条件
        if search_name:
            sql = f"{base_sql} WHERE `姓名` = %s"
            data = db.execute_query(sql, (search_name,))
        else:
            data = db.execute_query(base_sql)
            
        return jsonify({"success": True, "data": data})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

# 写入数据 API
@app.route('/api/data', methods=['POST'])
def add_data():
    db = Database()
    try:
        content = request.json.get('content')
        if not content:
            return jsonify({"success": False, "error": "Content required"}), 400
            
        db.execute_query(
            "INSERT INTO your_table (content) VALUES (%s)",
            (content,)
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=False)  # 生产环境应关闭debug