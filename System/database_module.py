import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Any

class Database:
    def __init__(self, db_path: str = "embroidery_system.db"):
        """
        初始化数据库连接
        
        Args:
            db_path: 数据库文件路径
        """
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self) -> sqlite3.Connection:
        """获取数据库连接"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # 启用字典访问
        return conn
    
    def init_database(self):
        """初始化数据库表结构"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 创建员工表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS employees (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    status TEXT DEFAULT 'active',
                    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建花型表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS patterns (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL UNIQUE,
                    price REAL NOT NULL,
                    create_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            
            # 创建工资记录表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS records (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    employee_id INTEGER NOT NULL,
                    pattern_id INTEGER NOT NULL,
                    record_date DATE NOT NULL,
                    count INTEGER NOT NULL,
                    total REAL NOT NULL,
                    special TEXT DEFAULT '',
                    note TEXT DEFAULT '',
                    create_time TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (employee_id) REFERENCES employees (id),
                    FOREIGN KEY (pattern_id) REFERENCES patterns (id)
                )
            ''')
            
            # 创建系统设置表
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL
                )
            ''')
            
            conn.commit()
            
            # 初始化默认数据
            self._init_default_data()
            
        except Exception as e:
            conn.rollback()
            raise e
        finally:
            conn.close()
    
    def _init_default_data(self):
        """初始化默认花型数据"""
        default_patterns = [
            ("盖布", 5.5),
            ("浮花", 5.5),
            ("棉盖", 5.5),
            ("棉", 5.0),
            ("藏网", 5.5),
            ("雕孔", 6.5),
            ("棉网", 5.5),
            ("水溶", 4.4),
            ("牛奶丝打孔", 6.5),
            ("网布", 5.5),
            ("玻璃纱", 5.2),
            ("盖网", 5.0)
        ]
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            for name, price in default_patterns:
                cursor.execute('''
                    INSERT OR IGNORE INTO patterns (name, price) 
                    VALUES (?, ?)
                ''', (name, price))
            
            conn.commit()
        except Exception as e:
            conn.rollback()
            print(f"初始化默认数据失败: {e}")
        finally:
            conn.close()
    
    # ==================== 员工管理 ====================
    
    def get_employees(self, search: str = "", order_by: str = "create_date DESC") -> List[Dict]:
        """
        获取员工列表
        
        Args:
            search: 搜索关键词
            order_by: 排序方式
            
        Returns:
            员工列表
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            sql = "SELECT * FROM employees WHERE 1=1"
            params = []
            
            if search:
                sql += " AND name LIKE ?"
                params.append(f"%{search}%")
            
            sql += f" ORDER BY {order_by}"
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
            
        finally:
            conn.close()
    
    def add_employee(self, name: str, status: str = "active") -> Dict:
        """
        添加员工
        
        Args:
            name: 员工姓名
            status: 员工状态
            
        Returns:
            操作结果
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO employees (name, status) 
                VALUES (?, ?)
            ''', (name, status))
            
            employee_id = cursor.lastrowid
            conn.commit()
            
            return {
                "success": True,
                "message": "员工添加成功",
                "data": {"id": employee_id, "name": name, "status": status}
            }
            
        except sqlite3.IntegrityError:
            conn.rollback()
            return {"success": False, "message": "员工姓名已存在"}
        except Exception as e:
            conn.rollback()
            return {"success": False, "message": f"添加失败: {str(e)}"}
        finally:
            conn.close()
    
    def update_employee(self, employee_id: int, name: str, status: str) -> Dict:
        """
        更新员工信息
        
        Args:
            employee_id: 员工ID
            name: 员工姓名
            status: 员工状态
            
        Returns:
            操作结果
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE employees 
                SET name = ?, status = ? 
                WHERE id = ?
            ''', (name, status, employee_id))
            
            if cursor.rowcount == 0:
                return {"success": False, "message": "员工不存在"}
            
            conn.commit()
            return {"success": True, "message": "员工信息更新成功"}
            
        except sqlite3.IntegrityError:
            conn.rollback()
            return {"success": False, "message": "员工姓名已存在"}
        except Exception as e:
            conn.rollback()
            return {"success": False, "message": f"更新失败: {str(e)}"}
        finally:
            conn.close()
    
    def delete_employee(self, employee_id: int) -> Dict:
        """
        删除员工
        
        Args:
            employee_id: 员工ID
            
        Returns:
            操作结果
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 检查是否有相关工资记录
            cursor.execute("SELECT COUNT(*) FROM records WHERE employee_id = ?", (employee_id,))
            record_count = cursor.fetchone()[0]
            
            if record_count > 0:
                return {"success": False, "message": f"无法删除，该员工有 {record_count} 条工资记录"}
            
            cursor.execute("DELETE FROM employees WHERE id = ?", (employee_id,))
            
            if cursor.rowcount == 0:
                return {"success": False, "message": "员工不存在"}
            
            conn.commit()
            return {"success": True, "message": "员工删除成功"}
            
        except Exception as e:
            conn.rollback()
            return {"success": False, "message": f"删除失败: {str(e)}"}
        finally:
            conn.close()
    
    # ==================== 花型管理 ====================
    
    def get_patterns(self, search: str = "", order_by: str = "create_date DESC") -> List[Dict]:
        """
        获取花型列表
        
        Args:
            search: 搜索关键词
            order_by: 排序方式
            
        Returns:
            花型列表
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            sql = "SELECT * FROM patterns WHERE 1=1"
            params = []
            
            if search:
                sql += " AND name LIKE ?"
                params.append(f"%{search}%")
            
            sql += f" ORDER BY {order_by}"
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
            
        finally:
            conn.close()
    
    def add_pattern(self, name: str, price: float) -> Dict:
        """
        添加花型
        
        Args:
            name: 花型名称
            price: 花型单价
            
        Returns:
            操作结果
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT INTO patterns (name, price) 
                VALUES (?, ?)
            ''', (name, price))
            
            pattern_id = cursor.lastrowid
            conn.commit()
            
            return {
                "success": True,
                "message": "花型添加成功",
                "data": {"id": pattern_id, "name": name, "price": price}
            }
            
        except sqlite3.IntegrityError:
            conn.rollback()
            return {"success": False, "message": "花型名称已存在"}
        except Exception as e:
            conn.rollback()
            return {"success": False, "message": f"添加失败: {str(e)}"}
        finally:
            conn.close()
    
    def update_pattern(self, pattern_id: int, name: str, price: float) -> Dict:
        """
        更新花型信息
        
        Args:
            pattern_id: 花型ID
            name: 花型名称
            price: 花型单价
            
        Returns:
            操作结果
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                UPDATE patterns 
                SET name = ?, price = ? 
                WHERE id = ?
            ''', (name, price, pattern_id))
            
            if cursor.rowcount == 0:
                return {"success": False, "message": "花型不存在"}
            
            conn.commit()
            return {"success": True, "message": "花型信息更新成功"}
            
        except sqlite3.IntegrityError:
            conn.rollback()
            return {"success": False, "message": "花型名称已存在"}
        except Exception as e:
            conn.rollback()
            return {"success": False, "message": f"更新失败: {str(e)}"}
        finally:
            conn.close()
    
    def delete_pattern(self, pattern_id: int) -> Dict:
        """
        删除花型
        
        Args:
            pattern_id: 花型ID
            
        Returns:
            操作结果
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 检查是否有相关工资记录
            cursor.execute("SELECT COUNT(*) FROM records WHERE pattern_id = ?", (pattern_id,))
            record_count = cursor.fetchone()[0]
            
            if record_count > 0:
                return {"success": False, "message": f"无法删除，该花型有 {record_count} 条工资记录"}
            
            cursor.execute("DELETE FROM patterns WHERE id = ?", (pattern_id,))
            
            if cursor.rowcount == 0:
                return {"success": False, "message": "花型不存在"}
            
            conn.commit()
            return {"success": True, "message": "花型删除成功"}
            
        except Exception as e:
            conn.rollback()
            return {"success": False, "message": f"删除失败: {str(e)}"}
        finally:
            conn.close()
    
    # ==================== 工资记录管理 ====================
    
    def get_records(self, employee_id: int = None, pattern_id: int = None, 
                   start_date: str = None, end_date: str = None, 
                   order_by: str = "record_date DESC") -> List[Dict]:
        """
        获取工资记录列表
        
        Args:
            employee_id: 员工ID
            pattern_id: 花型ID
            start_date: 开始日期
            end_date: 结束日期
            order_by: 排序方式
            
        Returns:
            工资记录列表
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            sql = '''
                SELECT r.*, e.name as employee_name, p.name as pattern_name, p.price
                FROM records r
                JOIN employees e ON r.employee_id = e.id
                JOIN patterns p ON r.pattern_id = p.id
                WHERE 1=1
            '''
            params = []
            
            if employee_id:
                sql += " AND r.employee_id = ?"
                params.append(employee_id)
            
            if pattern_id:
                sql += " AND r.pattern_id = ?"
                params.append(pattern_id)
            
            if start_date:
                sql += " AND r.record_date >= ?"
                params.append(start_date)
            
            if end_date:
                sql += " AND r.record_date <= ?"
                params.append(end_date)
            
            sql += f" ORDER BY {order_by}"
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
            
        finally:
            conn.close()
    
    def add_record(self, employee_id: int, pattern_id: int, record_date: str, 
                  count: int, special: str = "", note: str = "") -> Dict:
        """
        添加工资记录
        
        Args:
            employee_id: 员工ID
            pattern_id: 花型ID
            record_date: 记录日期
            count: 针数
            special: 特殊标记
            note: 备注
            
        Returns:
            操作结果
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 获取花型单价
            cursor.execute("SELECT price FROM patterns WHERE id = ?", (pattern_id,))
            pattern = cursor.fetchone()
            if not pattern:
                return {"success": False, "message": "花型不存在"}
            
            price = pattern[0]
            total = count * price
            
            cursor.execute('''
                INSERT INTO records (employee_id, pattern_id, record_date, count, total, special, note)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (employee_id, pattern_id, record_date, count, total, special, note))
            
            record_id = cursor.lastrowid
            conn.commit()
            
            return {
                "success": True,
                "message": "工资记录添加成功",
                "data": {
                    "id": record_id,
                    "employee_id": employee_id,
                    "pattern_id": pattern_id,
                    "record_date": record_date,
                    "count": count,
                    "total": total,
                    "special": special,
                    "note": note
                }
            }
            
        except Exception as e:
            conn.rollback()
            return {"success": False, "message": f"添加失败: {str(e)}"}
        finally:
            conn.close()
    
    def update_record(self, record_id: int, employee_id: int, pattern_id: int, 
                     record_date: str, count: int, special: str = "", note: str = "") -> Dict:
        """
        更新工资记录
        
        Args:
            record_id: 记录ID
            employee_id: 员工ID
            pattern_id: 花型ID
            record_date: 记录日期
            count: 针数
            special: 特殊标记
            note: 备注
            
        Returns:
            操作结果
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 获取花型单价
            cursor.execute("SELECT price FROM patterns WHERE id = ?", (pattern_id,))
            pattern = cursor.fetchone()
            if not pattern:
                return {"success": False, "message": "花型不存在"}
            
            price = pattern[0]
            total = count * price
            
            cursor.execute('''
                UPDATE records 
                SET employee_id = ?, pattern_id = ?, record_date = ?, count = ?, total = ?, special = ?, note = ?
                WHERE id = ?
            ''', (employee_id, pattern_id, record_date, count, total, special, note, record_id))
            
            if cursor.rowcount == 0:
                return {"success": False, "message": "记录不存在"}
            
            conn.commit()
            return {"success": True, "message": "工资记录更新成功"}
            
        except Exception as e:
            conn.rollback()
            return {"success": False, "message": f"更新失败: {str(e)}"}
        finally:
            conn.close()
    
    def delete_record(self, record_id: int) -> Dict:
        """
        删除工资记录
        
        Args:
            record_id: 记录ID
            
        Returns:
            操作结果
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("DELETE FROM records WHERE id = ?", (record_id,))
            
            if cursor.rowcount == 0:
                return {"success": False, "message": "记录不存在"}
            
            conn.commit()
            return {"success": True, "message": "工资记录删除成功"}
            
        except Exception as e:
            conn.rollback()
            return {"success": False, "message": f"删除失败: {str(e)}"}
        finally:
            conn.close()
    
    # ==================== 统计报表 ====================
    
    def get_daily_summary(self, start_date: str = None, end_date: str = None) -> List[Dict]:
        """
        获取日工资汇总
        
        Args:
            start_date: 开始日期
            end_date: 结束日期
            
        Returns:
            日汇总数据
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            sql = '''
                SELECT 
                    r.record_date,
                    e.name as employee_name,
                    p.name as pattern_name,
                    SUM(r.count) as total_count,
                    SUM(r.total) as total_amount
                FROM records r
                JOIN employees e ON r.employee_id = e.id
                JOIN patterns p ON r.pattern_id = p.id
                WHERE 1=1
            '''
            params = []
            
            if start_date:
                sql += " AND r.record_date >= ?"
                params.append(start_date)
            
            if end_date:
                sql += " AND r.record_date <= ?"
                params.append(end_date)
            
            sql += " GROUP BY r.record_date, r.employee_id, r.pattern_id ORDER BY r.record_date DESC"
            
            cursor.execute(sql, params)
            rows = cursor.fetchall()
            
            return [dict(row) for row in rows]
            
        finally:
            conn.close()
    
    def get_monthly_summary(self, year: int, month: int) -> Dict:
        """
        获取月工资汇总
        
        Args:
            year: 年份
            month: 月份
            
        Returns:
            月汇总数据
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # 获取指定月份的数据
            start_date = f"{year}-{month:02d}-01"
            if month == 12:
                end_date = f"{year+1}-01-01"
            else:
                end_date = f"{year}-{month+1:02d}-01"
            
            sql = '''
                SELECT 
                    e.name as employee_name,
                    p.name as pattern_name,
                    SUM(r.count) as total_count,
                    SUM(r.total) as total_amount
                FROM records r
                JOIN employees e ON r.employee_id = e.id
                JOIN patterns p ON r.pattern_id = p.id
                WHERE r.record_date >= ? AND r.record_date < ?
                GROUP BY r.employee_id, r.pattern_id
                ORDER BY e.name, p.name
            '''
            
            cursor.execute(sql, (start_date, end_date))
            rows = cursor.fetchall()
            
            # 组织数据格式
            data = {}
            patterns = set()
            
            for row in rows:
                employee = row['employee_name']
                pattern = row['pattern_name']
                count = row['total_count']
                amount = row['total_amount']
                
                if employee not in data:
                    data[employee] = {}
                
                data[employee][pattern] = {
                    'count': count,
                    'amount': amount
                }
                patterns.add(pattern)
            
            return {
                'data': data,
                'patterns': sorted(list(patterns)),
                'year': year,
                'month': month
            }
            
        finally:
            conn.close()
    
    # ==================== 设置管理 ====================
    
    def get_setting(self, key: str) -> Optional[str]:
        """
        获取设置值
        
        Args:
            key: 设置键
            
        Returns:
            设置值
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("SELECT value FROM settings WHERE key = ?", (key,))
            row = cursor.fetchone()
            return row[0] if row else None
            
        finally:
            conn.close()
    
    def set_setting(self, key: str, value: str) -> bool:
        """
        设置值
        
        Args:
            key: 设置键
            value: 设置值
            
        Returns:
            是否成功
        """
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute('''
                INSERT OR REPLACE INTO settings (key, value) 
                VALUES (?, ?)
            ''', (key, value))
            
            conn.commit()
            return True
            
        except Exception as e:
            conn.rollback()
            print(f"设置失败: {e}")
            return False
        finally:
            conn.close()
