from flask import Blueprint, request, jsonify
from database import Database
import numpy as np

data_bp = Blueprint('data', __name__)

@data_bp.route('/data', methods=['GET'])
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


@data_bp.route('/data', methods=['POST'])
def add_data():
    #获取Json文件并转换为数组
    content = request.json
    key_value_list = np.array([list(item) for item in content.items()])
    second_column = key_value_list[:,1].tolist()

    db = Database()
    try:
        if not content:
            return jsonify({"success": False, "error": "Content required"}), 400
            
        db.execute_query(
            "INSERT INTO Sheet1 VALUES (%s,%s,%s)",
            tuple(second_column)
        )
        return jsonify({"success": True})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()