# app.py - Flask 版通讯录（SQLite + 响应式 UI）
from flask import Flask, render_template, request, redirect, url_for, flash
import sqlite3
from datetime import datetime
import os

app = Flask(__name__)
app.secret_key = "contacts_secret_key"
DB_NAME = "contacts.db"

def init_db():
    """初始化数据库"""
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''
        CREATE TABLE IF NOT EXISTS contacts (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            name TEXT NOT NULL,
            phone TEXT NOT NULL,
            created_at TEXT
        )
    ''')
    conn.commit()
    conn.close()

def get_db():
    """获取数据库连接"""
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn

@app.route('/')
def index():
    """主页：显示联系人列表"""
    conn = get_db()
    contacts = conn.execute('SELECT * FROM contacts ORDER BY created_at DESC').fetchall()
    conn.close()
    return render_template('index.html', contacts=contacts)

@app.route('/add', methods=['POST'])
def add_contact():
    """添加联系人"""
    name = request.form['name'].strip()
    phone = request.form['phone'].strip()
    
    if not name or not phone:
        flash("姓名和电话不能为空！", "error")
        return redirect(url_for('index'))
    
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = get_db()
    conn.execute('INSERT INTO contacts (name, phone, created_at) VALUES (?, ?, ?)',
                 (name, phone, created_at))
    conn.commit()
    conn.close()
    
    flash("添加成功！", "success")
    return redirect(url_for('index'))

@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_contact(id):
    """编辑联系人"""
    conn = get_db()
    
    if request.method == 'POST':
        name = request.form['name'].strip()
        phone = request.form['phone'].strip()
        
        if not name or not phone:
            flash("姓名和电话不能为空！", "error")
            return redirect(url_for('edit_contact', id=id))
        
        conn.execute('UPDATE contacts SET name = ?, phone = ? WHERE id = ?',
                     (name, phone, id))
        conn.commit()
        conn.close()
        flash("修改成功！", "success")
        return redirect(url_for('index'))
    
    # GET 请求：显示编辑表单
    contact = conn.execute('SELECT * FROM contacts WHERE id = ?', (id,)).fetchone()
    conn.close()
    
    if not contact:
        flash("联系人不存在！", "error")
        return redirect(url_for('index'))
    
    return render_template('edit.html', contact=contact)

@app.route('/delete/<int:id>', methods=['POST'])
def delete_contact(id):
    """删除联系人"""
    conn = get_db()
    contact = conn.execute('SELECT * FROM contacts WHERE id = ?', (id,)).fetchone()
    
    if contact:
        conn.execute('DELETE FROM contacts WHERE id = ?', (id,))
        conn.commit()
        flash("删除成功！", "success")
    else:
        flash("联系人不存在！", "error")
    
    conn.close()
    return redirect(url_for('index'))

if __name__ == '__main__':
    init_db()
    print("通讯录启动成功：http://127.0.0.1:5000")
    app.run(debug=True, host='0.0.0.0', port=5000)