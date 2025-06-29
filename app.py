from datetime import datetime
from functools import wraps
import os
from flask import Flask, flash, redirect, render_template, request, session
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.secret_key = os.environ.get('SECRET_KEY', 'DEFAULT_SECRET_KEY')
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

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect('/login')
        return f(*args, **kwargs)
    return decorated_function

# トップページ（タスクリスト）
@app.route('/')
@login_required
def index():
    # if 'user_id' not in session:
    #     return redirect('/login')
    todos = Todo.query.filter_by(user_id=session['user_id']).all()
    return render_template('index.html', todos=todos)

# タスクの追加
@app.route('/add', methods=['POST'])
@login_required
def add():
    # if 'user_id' not in session:
    #     return redirect('/login')
    task_text = request.form['task']
    new_todo = Todo(task=task_text, user_id=session['user_id'])
    db.session.add(new_todo)
    db.session.commit()
    return redirect('/')

# タスクの削除
@app.route('/delete/<int:todo_id>')
@login_required
def delete(todo_id):
    # if 'user_id' not in session:
    #     return redirect('/login')
    todo = Todo.query.get(todo_id)
    if todo:
        db.session.delete(todo)
        db.session.commit()
    return redirect('/')

@app.route('/inventory')
@login_required
def inventory():
    items = Inventory.query.all()
    return render_template('inventory.html', items=items)

@app.route('/inventory/add', methods=['POST'])
@login_required
def add_inventory():
    # if 'user_id' not in session:
    #     return redirect('/login')
    category = request.form['category']
    item_name = request.form['name']
    quantity = int(request.form['quantity'])
    expire_date = request.form.get('expire_date')
    expire_date = datetime.strptime(expire_date, '%Y-%m-%d') if expire_date else None
    new_item = Inventory(
        category=category, item_name=item_name, quantity=quantity, expire_date=expire_date, user_id=session['user_id']
    )
    db.session.add(new_item)
    db.session.commit()
    return redirect('/inventory')

@app.route('/inventory/update/<int:item_id>', methods=['POST'])
@login_required
def update_inventory(item_id):
    item = Inventory.query.get(item_id)
    # if item and item.user_id == session['user_id']:
    if item:
        try:
            quantity = request.form.get('quantity')
            expire_date = request.form.get('expire_date')

            if quantity is not None and quantity != "":
                item.quantity = int(quantity)
            if expire_date:
                item.expire_date = datetime.strptime(expire_date, '%Y-%m-%d')
            else:
                item.expire_date = None
            db.session.commit()
            flash("Inventory item updated successfully!", "success")
        except ValueError:
            flash("Invalid quantity or date format. Please check your input.", "danger")
    return redirect('/inventory')

@app.route('/inventory/delete/<int:item_id>')
@login_required
def delete_inventory(item_id):
    # if 'user_id' not in session:
    #     return redirect('/login')
    item = Inventory.query.get(item_id)
    if item:
        db.session.delete(item)
        db.session.commit()
    return redirect('/inventory')

@app.route('/users', methods=['GET', 'POST'])
def users():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if not username or not password:
            return "ユーザー名とパスワードは必須です", 400
        if User.query.count() >= 2:
            return "ユーザーは2名までです", 400
        if User.query.filter_by(username=username).first():
            return "そのユーザー名は既に使われています", 400
        new_user = User(username=username, password=password)
        db.session.add(new_user)
        db.session.commit()
        return redirect('/users')
    users = User.query.all()
    return render_template('users.html', users=users)

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username, password=password).first()
        if user:
            session['user_id'] = user.id
            return redirect('/')
        return 'ログイン失敗'
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.clear()
    return redirect('/login')

if __name__ == '__main__':
    # 初回のみ以下を実行してテーブルを作成
    # with app.app_context():
    #     db.create_all()
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
