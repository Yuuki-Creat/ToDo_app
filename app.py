import os
from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy


app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class Task(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(200), nullable=False)

# トップページ（タスクリスト）
@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

# タスクの追加
app.route('/add', methods=['POST'])
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

if __name__ == '__name__':
    # 初回のみ以下を実行してテーブルを作成
    with app.app_context():
        db.create_all()
    app.run(debug=True)
