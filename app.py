import os
from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(50), unique=True, nullable=False)
    password = db.Column(db.String(100), nullable=False)

class Todo(db.Model):
    __tablename__ = 'todos'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    task = db.Column(db.Text, nullable=False)
    due_date = db.Column(db.Date)
    is_done = db.Column(db.Boolean, default=False)

class Inventory(db.Model):
    __tablename__ = 'inventory'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id', ondelete='CASCADE'))
    item_name = db.Column(db.String(100), nullable=False)
    quantity = db.Column(db.Integer, default=0)
    category = db.Column(db.String(50))
    expire_date = db.Column(db.Date)

# トップページ（タスクリスト）
@app.route('/')
def index():
    tasks = Todo.query.all()
    return render_template('index.html', tasks=tasks)

# タスクの追加
@app.route('/add', methods=['POST'])
def add():
    content = request.form['content']
    new_todo = Todo(content=content)
    db.session.add(new_todo)
    db.session.commit()
    return redirect('/')

# タスクの削除
@app.route('/delete/<int:todo_id>')
def delete(todo_id):
    todo = Todo.query.get(todo_id)
    db.session.delete(todo)
    db.session.commit()
    return redirect('/')

@app.route('/inventory')
def inventory():
    items = Inventory.query.all()
    return render_template('inventory.html', items=items)

@app.route('/inventory/add', methods=['POST'])
def add_inventory():
    name = request.form['name']
    quantity = int(request.form['quantity'])
    new_item = Inventory(item_name=name, quantity=quantity)
    db.session.add(new_item)
    db.session.commit()
    return redirect('/inventory')

@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if User.query.count() >= 2:
            return "ユーザーは2名までです"
        new_user = User(username=username, password=password)
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
