import os
# 产品进度日志相关接口
from flask import Blueprint, request, jsonify
from database import Database
from config import Config,current_dir

# 创建蓝图对象，注册到Flask主应用
product_schedule_bp = Blueprint('product_schedule', __name__)

# =========================
# 阶段一：产品进度查询接口
# =========================
# 输入：GET请求，参数为修理方式（如 /product_schedule?修理方式=xxx）
# 输出：产品各阶段统计、当前阶段统计、完成比率等
@product_schedule_bp.route('/product_schedule', methods=['GET'])
def get_product_schedule_data():
    db = Database()  # 创建数据库连接
    args = ['修理方式']  # 查询参数名
    column_name = ['修理方式']  # 数据库列名
    object_array = [None]*len(args)

    try:
        # 读取数据库配置
        DATABASE_product_schedule = Config.DATABASE_product_schedule
        DATABASE_product_schedule_fixmethod = Config.DATABASE_product_schedule_fixmethod

        # 读取SQL模板
        sql_path = os.path.join(current_dir,'routes/sql/product_schedule.sql')  
        with open(sql_path, 'r', encoding='utf-8') as f:
            _base_sql = f.read()
        base_sql = _base_sql.replace('{{ database_a }}', DATABASE_product_schedule)
        base_sql_1 = _base_sql.replace('{{ database_a }}', DATABASE_product_schedule_fixmethod)

        # 获取请求参数
        for index in range(len(args)):
            object_array[index] = request.args.get(args[index])

        # 拼接SQL条件
        # 如果object_array中有非None值，则添加WHERE条件
        # 否则不添加条件
        if object_array[0] == '':
            object_array = [None] * len(object_array)
        add_sql = ""
        if object_array and any(obj is not None and obj != '' for obj in object_array):
            add_sql = " WHERE"
            _counter = 0
            for index in range(len(object_array)):
                if object_array[index] is not None and object_array[index] != '':
                    if _counter > 0:
                        add_sql = f"{add_sql} AND"
                    add_sql = f"{add_sql} a.`{column_name[index]}` = '{object_array[index]}'"
                    _counter += 1

        #print(base_sql + add_sql)
        data = db.execute_query(base_sql + add_sql)  # 查询产品进度主表
        #print(data)
        data_fixmethod = db.execute_query(base_sql_1)  # 查询所有修理阶段

        # 统计阶段信息
        stages_origin = []
        for item in data_fixmethod:
            d = item.get('stage')
            if d not in stages_origin:
                stages_origin.append(d)
        stages_select = []
        stages_current = [item.get('当前维修进度') for item in data if item.get('当前维修进度')]
        stats = {stage: {0: 0, 1: 0, 2: 0} for stage in stages_origin}
        count_stages_current = {stage: 0 for stage in stages_select}

        # 统计每个阶段的状态数量
        for item in data:
            for stage in stages_origin:
                value = item.get(stage)
                if isinstance(value, int) and value in (0, 1, 2):
                    stats[stage][value] += 1

        # 选出未完工的阶段
        for stage in stages_origin:
            if stats[stage][2] < len(data):
                stages_select.append(stage)

        # 计算每个阶段的完成比率
        stage_complete_ratio = {stage: 0 for stage in stages_select}

        # 统计当前阶段数量
        for stage in stages_current:
            count_stages_current[stage] = count_stages_current.get(stage, 0) + 1
        # 计算每个阶段的完成比率
        for stage in stages_select:
            if stats[stage][1] != 0:
                stage_complete_ratio[stage] = stats[stage][1] / (stats[stage][0] + stats[stage][1])
            else:
                stage_complete_ratio[stage] = 0

        # 转为数组，便于前端展示
        # 对当前阶段数量进行补全，填充0
        count_stages_current_full = {stage: 0 for stage in stages_select}
        for stage in stages_select:
            count_stages_current_full[stage] = count_stages_current.get(stage, 0)
        count_stages_current_array = list(count_stages_current_full.values())

        stage_complete_ratio_array = list(stage_complete_ratio.values())

        # 输出结果
        return jsonify({
            "success": True,
            "stages_select": stages_select,  # 阶段名数组
            "count_stages_current_array": count_stages_current_array,  # 当前阶段数量数组
            "stage_complete_ratio_array": stage_complete_ratio_array,  # 阶段完成比率数组
            "total_count": len(data)  # 总产品数
            
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

# =========================
# 阶段二：查询所有产品信息
# =========================
# 输入：GET请求，可选参数修理方式
# 输出：所有产品的详细信息（列表）
@product_schedule_bp.route('/product_information_all', methods=['GET'])
def product_information_all():
    db = Database()
    args = ['修理方式']
    column_name = ['修理方式']
    object_array = [None]*len(args)

    try:
        DATABASE_product_schedule = Config.DATABASE_product_schedule
        sql_path = os.path.join(current_dir,'routes/sql/product_schedule.sql')
        with open(sql_path, 'r', encoding='utf-8') as f:
            _base_sql = f.read()
        base_sql = _base_sql.replace('{{ database_a }}', DATABASE_product_schedule)
        #print(base_sql)
        data = db.execute_query(base_sql)
        #print(data)

        return jsonify({
            "success": True,
            "data": data
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

# =========================
# 阶段四：增加或更新产品信息
# =========================
# 输入：POST请求，body为产品信息JSON
# 输出：操作成功或失败的消息
@product_schedule_bp.route('/add_product_information', methods=['POST'])
def add_product_information():
    db = Database()
    try:
        DATABASE_product_schedule = Config.DATABASE_product_schedule

        

        # 获取前端传来的产品信息
        data = request.get_json()
        #print(data)

        sql_path = os.path.join(current_dir, 'routes/sql/product_schedule.sql')
        with open(sql_path, 'r', encoding='utf-8') as f:
            _base_sql = f.read()
        base_sql = _base_sql.replace('{{ database_a }}', DATABASE_product_schedule)
        add_sql_1 = "\nWHERE `产品id` = {}".format(data.get('产品id')) if data.get('产品id') else ""
        base_sql = base_sql + add_sql_1
        data_origin = db.execute_query(base_sql)


        # 获取表字段
        sql = f"SHOW COLUMNS FROM {DATABASE_product_schedule}"
        fields_info = db.execute_query(sql)
        fields = [row['Field'] for row in fields_info]

        # 插入时所有字段都要有（主键和必填字段不能为空，否则插入会报错）
        values = [data.get(f, None) for f in fields]
        def sql_value(v):
            if v is None:
                return 'NULL'
            elif v == "":
                return 'NULL'
            return f'"{v}"'
        values_placeholders = ','.join(sql_value(v) for v in values)

        # 更新时只更新有值的字段
        update_fields = ', '.join(
            f"`{f}`=VALUES(`{f}`)" for f, v in zip(fields, values)
            if f != "产品id" and v is not None and v != ""
        )
        # 获取前端传来的“当前状态”字段名
        if data_origin and isinstance(data_origin, list):
            current_status_field = data_origin[0].get('当前维修进度')
        else:
            current_status_field = None
        add_sql = ""
        if current_status_field:
            add_sql = f", `{current_status_field}`=1"
        else:
            add_sql = ""

        # 拼接到 upsert_sql 的 update_fields 后面
        if update_fields:
            update_fields = update_fields + add_sql
        else:
            update_fields = add_sql[2:]  # 去掉前面的逗号和空格



        # 读取upsert SQL模板并填充
        upsert_sql_path = os.path.join(current_dir, 'routes/sql/upsert_parts.sql')
        with open(upsert_sql_path, 'r', encoding='utf-8') as f:
            upsert_sql_template = f.read()
        upsert_sql = upsert_sql_template \
            .replace('{{ table_name }}', DATABASE_product_schedule) \
            .replace('{{ fields }}', ','.join(f'`{f}`' for f in fields)) \
            .replace('{{ values_placeholders }}', values_placeholders) \
            .replace('{{ update_fields }}', update_fields)
        print(upsert_sql)
        data = db.execute_query(upsert_sql)
        return jsonify({"success": True, "message": "操作成功"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()

# =========================
# 阶段五：删除产品信息
# =========================
# 输入：POST请求，body为{"产品id":xxx}
# 输出：操作成功或失败的消息
@product_schedule_bp.route('/delete_product_information', methods=['POST'])
def delete_product_information():
    db = Database()
    try:
        DATABASE_product_schedule = Config.DATABASE_product_schedule

        # 获取前端传来的产品id
        data = request.get_json()
        print(data)
        product_id = data.get('产品id')

        if not product_id:
            return jsonify({"success": False, "error": "产品id不能为空"}), 400

        # 读取删除SQL模板并填充
        delete_sql = 'routes/sql/delete.sql'
        with open(delete_sql, 'r', encoding='utf-8') as f:
            delete_sql_template = f.read()
        delete_sql = delete_sql_template\
            .replace('{{ table_name }}', DATABASE_product_schedule) \
            .replace('{{ key_field }}', '产品id')\
            .replace('{{ key_value }}', f'"{product_id}"')
        print(delete_sql)
        db.execute_query(delete_sql)

        return jsonify({"success": True, "message": "删除成功"})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()
