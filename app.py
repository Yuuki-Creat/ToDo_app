import os
from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    tasks = db.relationship('Task', backref='user', lazy=True)

class InventoryItem(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, nullable=False, default=1)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)

# トップページ（タスクリスト）
@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

# タスクの追加
@app.route('/add', methods=['POST'])
def add():
    content = request.form['content']
    new_task = Task(content=content)
    db.session.add(new_task)
    db.session.commit()
    return redirect('/')

# タスクの削除
@app.route('/delete/<int:task_id>')
def delete(task_id):
    task = Task.query.get(task_id)
    db.session.delete(task)
    db.session.commit()
    return redirect('/')

@app.route('/inventory')
def inventory():
    items = InventoryItem.query.all()
    return render_template('inventory.html', items=items)

@app.route('/inventory/add', methods=['POST'])
def add_inventory():
    name = request.form['name']
    quantity = int(request.form['quantity'])
    new_item = InventoryItem(name=name, quantity=quantity)
    db.session.add(new_item)
    db.session.commit()
    return redirect('/inventory')

@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        username = request.form['username']
        if User.query.count() >= 2:
            return "ユーザーは2名までです"
        new_user = User(username=username)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/users')
    users = User.query.all()
    return render_template('users.html', users=users)

if __name__ == '__main__':
    # 初回のみ以下を実行してテーブルを作成
    with app.app_context():
        db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
