#产品进度日志
from flask import Blueprint, request, jsonify
from database import Database
from config import Config

product_schedule_bp = Blueprint('product_schedule', __name__)

# 产品进度查询
# 获取产品进度数据
@product_schedule_bp.route('/product_schedule', methods=['GET'])
def get_product_schedule_data():
    # 创建数据库连接
    # 这里的Database类需要根据实际情况进行实现
    db = Database()
    # 定义查询参数和对应的列名
    # 这里的参数需要和前端请求的参数一致
    args = ['修理方式']
    #对应的列名
    # 这里的列名需要和数据库中的列名一致
    column_name = ['修理方式']
    object_array = [None]*len(args)

    try:
        # 使用app.config获取配置
        DATABASE_product_schedule = Config.DATABASE_product_schedule
        DATABASE_product_schedule_fixmethod = Config.DATABASE_product_schedule_fixmethod
        # 原实现逻辑...
        # 基础SQL
        sql_path = 'routes/sql/product_schedule.sql'
        with open(sql_path, 'r', encoding='utf-8') as f:
            _base_sql = f.read()
        base_sql = _base_sql.replace('{{ database_a }}', DATABASE_product_schedule)
        base_sql_1 = _base_sql.replace('{{ database_a }}', DATABASE_product_schedule_fixmethod)
        # 获取查询参数（如：/api/data?name=刘展鹏）
        # 这里可以根据实际情况修改参数
        # 例如，如果前端传递的参数是修理方式，可以这样获取
        # 这里的参数需要和前端请求的参数一致
        for index in range(len(args)):
            object_array[index] = request.args.get(args[index])
            
        add_sql = ""
        if object_array.count(None) != len(object_array):
            add_sql = " WHERE"
            _counter=0
            for index in range(len(object_array)):
                if object_array[index] != None and object_array[index] != '':
                    if _counter > 0:
                        #如果不是第一个条件，则添加 AND
                        add_sql =  f"{add_sql} AND"
                    add_sql = f"{add_sql} a.`{column_name[index]}` = '{object_array[index]}'"
                    _counter = _counter+1
        print(base_sql+add_sql)      
        data = db.execute_query(base_sql+add_sql)
        #从数据库中拿所有的修理阶段
        data_fixmethod = db.execute_query(base_sql_1)
        # 处理数据
        # 这里可以根据需要对数据进行处理
         # 初始化统计字典
        #创建包含所有阶段的数组
        stages_origin = []
        for item in data_fixmethod:
            d = item.get('stage')
            if d not in stages_origin:
                stages_origin.append(d)
        #包含该修理方式选择的阶段的数组 需要return给前端
        stages_select = []
        #统计当前阶段的数组
        stages_current = []
        # 初始化统计字典
         # 统计每个阶段的0/1/2数量
         # 这里假设数据是一个列表，每个元素是一个字典，字典的键是阶段名称，值是对应的0/1/2
         # 示例数据格式：data = [{'阶段 A': 0, '阶段 B': 1, ...}, {...}, ...]
        stats = {stage: {0: 0, 1: 0, 2: 0} for stage in stages_origin}
        # 初始化当前阶段的计数器 需返回给前端 
        count_stages_current = {stage: 0 for stage in stages_select}
        # 遍历数据并统计
        for item in data:
            for stage in stages_origin:
                value = item.get(stage)
            # 确保值为整数且是0/1/2
                if isinstance(value, int) and value in (0, 1, 2):
                    stats[stage][value] += 1
        
        for stage in stages_origin:
            if stats[stage][2] == 0:
                stages_select.append(stage)
        # 初始化已选择阶段的完成比率 需返回给前端
        stage_complete_ratio = {stage: 0 for stage in stages_select}
        current = 0
        for item in data:
            for stage in stages_select:
                value = item.get(stage)
                # 确保值为整数且是0/1
                if isinstance(value, int) and value in (0, 1):
                    current = current + value
            # 如果当前阶段的计数器小于阶段选择的长度，则添加到当前阶段数组
            if current <= len(stages_select) - 1:
                stages_current.append(stages_select[current])
            else:
                # 如果当前阶段的计数器大于等于阶段选择的长度，则添加已完工
                # 这里假设已完工的阶段是一个特殊的状态
                stages_current.append('已完工')
            current = 0
        #统计当前阶段的数量
        # 遍历数据并统计当前阶段的数量
        for stage in stages_current:
                count_stages_current[stage] = count_stages_current.get(stage, 0) + 1
        for stage in stages_select:
            if stats[stage][1] != 0:
                stage_complete_ratio[stage] = stats[stage][1] / (stats[stage][0] + stats[stage][1])
            else:
                stage_complete_ratio[stage] = 0

        #前端友好，转成数组
        count_stages_current_full  = {stage: 0 for stage in stages_select}
        for stage in stages_select:
            count_stages_current_full[stage] = count_stages_current.get(stage, 0)        
        count_stages_current_array = list(count_stages_current_full.values())
        stage_complete_ratio_array = list(stage_complete_ratio.values())
            

        # 返回结果
        return jsonify({
            "success": True,
            "stages_select": stages_select,  # 你的数组
            "count_stages_current_array": count_stages_current_array,  
            "stage_complete_ratio_array": stage_complete_ratio_array,
            "total_count": len(data)  
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

#产品信息查询
#查询所有产品信息
@product_schedule_bp.route('/product_information_all', methods=['GET'])
def product_information_all():
    # 创建数据库连接
    # 这里的Database类需要根据实际情况进行实现
    db = Database()
    # 定义查询参数和对应的列名
    # 这里的参数需要和前端请求的参数一致
    args = ['修理方式']
    #对应的列名
    # 这里的列名需要和数据库中的列名一致
    column_name = ['修理方式']
    object_array = [None]*len(args)

    try:
        # 使用app.config获取配置
        DATABASE_product_schedule = Config.DATABASE_product_schedule
        # 原实现逻辑...
        # 基础SQL
        sql_path = 'routes/sql/product_schedule.sql'
        with open(sql_path, 'r', encoding='utf-8') as f:
            _base_sql = f.read()
        base_sql = _base_sql.replace('{{ database_a }}', DATABASE_product_schedule)
        print(base_sql)      
        data = db.execute_query(base_sql)

        # 返回结果
        return jsonify({
            "success": True,
            "data": data 
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

#根据选择的修理方式和当前阶段获取产品信息
@product_schedule_bp.route('/product_information_part', methods=['GET'])
def get_product_information_part():
    # 创建数据库连接
    # 这里的Database类需要根据实际情况进行实现
    db = Database()
    # 定义查询参数和对应的列名
    # 这里的参数需要和前端请求的参数一致
    args = ['修理方式','当前阶段']
    #对应的列名
    # 这里的列名需要和数据库中的列名一致
    column_name = ['修理方式', '当前阶段']
    object_array = [None]*len(args)

    try:
        # 使用app.config获取配置
        DATABASE_product_schedule = Config.DATABASE_product_schedule
        # 原实现逻辑...
        # 基础SQL
        sql_path = 'routes/sql/product_schedule.sql'
        with open(sql_path, 'r', encoding='utf-8') as f:
            _base_sql = f.read()
        base_sql = _base_sql.replace('{{ database_a }}', DATABASE_product_schedule)
        for index in range(len(args)):
            object_array[index] = request.args.get(args[index])
            
        add_sql = ""
        if object_array.count(None) != len(object_array):
            add_sql = " WHERE"
            _counter=0
            for index in range(len(object_array)):
                if object_array[index] != None and object_array[index] != '':
                    if _counter > 0:
                        #如果不是第一个条件，则添加 AND
                        add_sql =  f"{add_sql} AND"
                    add_sql = f"{add_sql} a.`{column_name[index]}` = '{object_array[index]}'"
                    _counter = _counter+1
        print(base_sql+add_sql)      
        data = db.execute_query(base_sql+add_sql)

        # 返回结果
        return jsonify({
            "success": True,
            "data": data 
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

#增加和更新产品
@product_schedule_bp.route('/add_product_information', methods=['POST'])
def add_product_information():
    db = Database()
    try:
        DATABASE_product_schedule = Config.DATABASE_product_schedule

        #获取客户端发来的数据
        data = request.get_json()
        print(data)
        #字段映射
        sql = f"SHOW COLUMNS FROM {DATABASE_product_schedule}"
        fields_info = db.execute_query(sql)
        fields = [row['Field'] for row in fields_info]
        values = [data.get(f, None) for f in fields]

        #读取SQL语言并结合数据进行填充
        upsert_sql_path = 'routes/sql/upsert_parts.sql'
        with open(upsert_sql_path, 'r', encoding='utf-8') as f:
            upsert_sql_template = f.read()
        upsert_sql = upsert_sql_template \
            .replace('{{ table_name }}', DATABASE_product_schedule) \
            .replace('{{ fields }}', ','.join(f'`{f}`' for f in fields)) \
            .replace('{{ values_placeholders }}',  ','.join(f'"{f}"' for f in values)) \
            .replace('{{ update_fields }}', ', '.join(f"`{f}`=VALUES(`{f}`)" for f in fields if f != "产品id"))

        print(upsert_sql)
        data = db.execute_query(upsert_sql)
        return jsonify({"success": True, "message": "操作成功"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

# 删除产品
@product_schedule_bp.route('/delete_product_information', methods=['POST'])
def delete_product_information():
    db = Database()
    try:
        DATABASE_product_schedule = Config.DATABASE_product_schedule

        #获取客户端发来的数据
        data = request.get_json()
        print(data)
        product_id = data.get('产品id')

        if not product_id:
            return jsonify({"success": False, "error": "产品id不能为空"}), 400

        #删除SQL语句
        delete_sql = 'routes/sql/delete_product.sql'
        with open(delete_sql, 'r', encoding='utf-8') as f:
            delete_sql_template = f.read()
        # 替换模板中的占位符        
        delete_sql = delete_sql_template.replace('{{ table_name }}', DATABASE_product_schedule) \
            .replace('{{ product_id }}', product_id)
        # 执行删除操作
        print(delete_sql)
        # 执行删除操作
        db.execute_query(delete_sql)

        return jsonify({"success": True, "message": "删除成功"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()