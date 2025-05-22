#产品进度日志
from flask import Blueprint, request, jsonify
from database import Database
from config import Config

product_schedule_bp = Blueprint('product_schedule', __name__)

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
            stages_current.append(stages_select[current-1])
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
            "stage_complete_ratio_array": stage_complete_ratio_array   
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()


@product_schedule_bp.route('/product_schedule_all', methods=['GET'])
def get_product_schedule_data_all():
    db = Database()
    try:
        DATABASE_product_schedule = Config.DATABASE_product_schedule
        sql_path = 'routes/sql/product_schedule.sql'
        with open(sql_path, 'r', encoding='utf-8') as f:
            _base_sql = f.read()
        base_sql = _base_sql.replace('{{ database_a }}', DATABASE_product_schedule)
        # 不加任何where条件，直接查全部
        data = db.execute_query(base_sql)
        return jsonify({
            "success": True,
            "data": data
        })
    except Exception as e:
        return jsonify({"success": False, "error": str(e)}), 500
    finally:
        db.close()