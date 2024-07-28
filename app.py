from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
import os
import redis

# Flaskアプリケーションの設定
app = Flask(__name__, static_folder='./img')

# データベースファイルの絶対パスを設定
base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, 'blog.db')
app.config['SQLALCHEMY_DATABASE_URI'] = f'sqlite:///{db_path}'

# Redisのホストを環境変数から取得
redis_host = os.environ.get("redis_host", "redis://localhost")
r = redis.from_url(redis_host)

# SQLAlchemyの設定
db = SQLAlchemy(app)

# 今日の日付を取得
today = datetime.today()
# 年と月を取得し、yyyy年 mm月 形式で表示
formatted_date = today.strftime('%Y年 %m月')

# データベースモデルの定義
class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_num = db.Column(db.String(50), nullable=False)
    user_name = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Tokyo')))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method in ['GET', 'HEAD']:
        posts = Post.query.all()
        return render_template('index.html', posts=posts, formatted_date=formatted_date)
    elif request.method == 'POST':
        room_num = request.form.get('room_num')
        user_name = request.form.get('user_name')
        new_post = Post(room_num=room_num, user_name=user_name)
        db.session.add(new_post)
        db.session.commit()
        return redirect('/')

@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        room_number = request.form.get('room_num')
        name = request.form.get('user_name')
        if not room_number or not name:
            error_message = '部屋番号と氏名は必須です。'
            return render_template('create.html', error_message=error_message)
        elif not room_number.isdigit():
            error_message = '部屋番号には数字のみを入力してください。'
            return render_template('create.html', error_message=error_message)
        elif not name.isalnum():
            error_message = '氏名には記号は含めないでください。'
            return render_template('create.html', error_message=error_message)
        else:
            post = Post(room_num=room_number, user_name=name)
            db.session.add(post)
            db.session.commit()
            return redirect('/')
    else:
        link_params = request.args.get('id', '0')
        post = Post.query.filter_by(id=link_params).first()
        if not post:
            return render_template('create.html', link_params=link_params)
        return render_template('update.html', post=post)

@app.route('/update/<int:id>', methods=['GET', 'POST'])
def update(id):
    post = Post.query.get(id)
    if request.method == 'GET':
        return render_template('update.html', post=post)
    else:
        post.room_num = request.form.get('room_num')
        post.user_name = request.form.get('user_name')
        db.session.commit()
        return redirect('/')

@app.route('/delete/<int:id>', methods=['GET'])
def delete(id):
    post = Post.query.get(id)
    db.session.delete(post)
    db.session.commit()
    return redirect('/')

@app.route('/count', methods=['GET', 'POST'])
def count():
    link_params = request.args.get('id')
    if link_params is None:
        return redirect('/')
    post = Post.query.get(link_params)
    if not post:
        return redirect(f'/create?id={link_params}')
    if request.method == 'GET':
        return render_template('count.html', post=post)
    else:
        return redirect('/')

@app.route('/quick')
def quick():
    return render_template('quick.html')

if __name__ == '__main__':
    app.run()
