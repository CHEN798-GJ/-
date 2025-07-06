from flask import Flask, request, jsonify
from database import Database
import json
import base64
import io
import pandas as pd
from datetime import datetime, timedelta
import calendar
from excel_handler import ExcelHandler

class APIServer:
    def __init__(self):
        """初始化API服务器"""
        self.app = Flask(__name__)
        self.db = Database()
        self.excel_handler = ExcelHandler(self.db)
        self.setup_routes()
    
    def setup_routes(self):
        """设置API路由"""
        
        # ==================== 员工管理API ====================
        
        @self.app.route('/api/employees', methods=['GET'])
        def get_employees():
            """获取员工列表"""
            search = request.args.get('search', '')
            order_by = request.args.get('order_by', 'create_date DESC')
            
            try:
                employees = self.db.get_employees(search, order_by)
                return jsonify({
                    'success': True,
                    'data': employees
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'获取员工列表失败: {str(e)}'
                }), 500
        
        @self.app.route('/api/employees', methods=['POST'])
        def add_employee():
            """添加员工"""
            data = request.get_json()
            
            if not data or not data.get('name'):
                return jsonify({
                    'success': False,
                    'message': '员工姓名不能为空'
                }), 400
            
            result = self.db.add_employee(
                name=data['name'],
                status=data.get('status', 'active')
            )
            
            return jsonify(result)
        
        @self.app.route('/api/employees/<int:employee_id>', methods=['PUT'])
        def update_employee(employee_id):
            """更新员工信息"""
            data = request.get_json()
            
            if not data or not data.get('name'):
                return jsonify({
                    'success': False,
                    'message': '员工姓名不能为空'
                }), 400
            
            result = self.db.update_employee(
                employee_id=employee_id,
                name=data['name'],
                status=data.get('status', 'active')
            )
            
            return jsonify(result)
        
        @self.app.route('/api/employees/<int:employee_id>', methods=['DELETE'])
        def delete_employee(employee_id):
            """删除员工"""
            result = self.db.delete_employee(employee_id)
            return jsonify(result)
        
        # ==================== 花型管理API ====================
        
        @self.app.route('/api/patterns', methods=['GET'])
        def get_patterns():
            """获取花型列表"""
            search = request.args.get('search', '')
            order_by = request.args.get('order_by', 'create_date DESC')
            
            try:
                patterns = self.db.get_patterns(search, order_by)
                return jsonify({
                    'success': True,
                    'data': patterns
                })
            except Exception as e:
                return jsonify({
                    'success': False,
                    'message': f'获取花型列表失败: {str(e)}'
                }), 500
        
        @self.app.route('/api/patterns', methods=['POST'])
        def add_pattern():
            """添加花型"""
            data = request.get_json()
            
            if not data or not data.get('name') or not data.get('price'):
                return jsonify({
                    'success': False,
                    'message': '花型名称和单价不能为空'
                }), 400
            
            try:
                price = float(data['price'])
                if price <= 0:
                    return jsonify({
                        'success': False,
                        'message': '花型单价必须大于0'
                    }), 400
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': '花型单价格式错误'
                }), 400
            
            result = self.db.add_pattern(
                name=data['name'],
                price=price
            )
            
            return jsonify(result)
        
        @self.app.route('/api/patterns/<int:pattern_id>', methods=['PUT'])
        def update_pattern(pattern_id):
            """更新花型信息"""
            data = request.get_json()
            
            if not data or not data.get('name') or not data.get('price'):
                return jsonify({
                    'success': False,
                    'message': '花型名称和单价不能为空'
                }), 400
            
            try:
                price = float(data['price'])
                if price <= 0:
                    return jsonify({
                        'success': False,
                        'message': '花型单价必须大于0'
                    }), 400
            except ValueError:
                return jsonify({
                    'success': False,
                    'message': '花型单价格式错误'
                }), 400
            
            result = self.db.update_pattern(
                pattern_id=pattern_id,
                name=data['name'],
                price=price
            )
            
            return jsonify(result)
        
        @self.app.route('/api/patterns/<int:pattern_id>', methods=['DELETE'])
        def delete_pattern(pattern_id):
            """删除花型"""
            result = self.db.delete_pattern(pattern_id)
            return jsonify(result)
        
        # ==================== 工资记录管理API ====================
        
        @self.app.route('/api/records', methods=['GET'])
        def get_records():
            """获取工资记录列表"""
            employee_id = request.args.get('employee_id', type=int)
            pattern_id = request.args.get('pattern_id', type=int)
            start_date = request.args.get('start_date')
            end_date = request.args.get('end_date')
            order_by = request.args.get('order_by', 'record_date DESC')
            
            try:
                records = self.db.get_records(
                    employee_id=