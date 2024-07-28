from flask import Flask
from flask import render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import pytz
#画像ﾌｫﾙﾀﾞｰの場所をstaticで指定
#app = Flask(__name__,static_folder='./img')
app = Flask(__name__,static_folder='./img')
#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///C:/Users/AHA02902/Desktop/2024作業実績/【徳洲会】HFWEBアプリ_おむつ管理/第2回/blog.db'

db = SQLAlchemy(app)

 # 今日の日付を取得
today = datetime.today()
# 年と月を取得し、yyyy mm 形式で表示
formatted_date = today.strftime('%Y年 %m月')

class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    room_num = db.Column(db.String(50), nullable=False)
    user_name = db.Column(db.String(300), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.now(pytz.timezone('Asia/Tokyo')))

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'GET':
        posts = Post.query.all()
        return render_template('index.html', posts=posts,formatted_date=formatted_date)
    elif request.method == 'POST':
        # フォームから送信されたデータを処理する
        room_num = request.form.get('room_num')
        user_name = request.form.get('user_name')
        # データベースに新しい投稿を追加するなどの処理を行う
        new_post = Post(room_num=room_num, user_name=user_name)
        db.session.add(new_post)
        db.session.commit()
        # データベースにデータを追加した後は、適切なリダイレクトなどを行う
        return redirect('/')


@app.route('/create', methods=['GET', 'POST'])
def create():
    if request.method == 'POST':
        room_number = request.form.get('room_num')
        name = request.form.get('user_name')

        # 入力値のチェック
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
            # 入力値が条件を満たしている場合は、登録処理を行う
            # ここでデータベースへの登録などの処理を実装します
            post = Post(room_num=room_number, user_name=name)
            db.session.add(post)
            db.session.commit()
            return redirect('/')

    else:
        # リンク先のURLを表示するためにテンプレートに渡す
        link_params = request.args.get('id','0')
            # IDに一致する投稿を取得
        post = Post.query.filter_by(id=link_params).first()

        # 取得した投稿が存在しない場合にエラーを出力
        if not post:
            return render_template('create.html',link_params=link_params)
        # 取得した投稿が存在しない場合にエラーを出力
        return render_template('update.html', post=post)


#@app.route('/<int:id>/update', methods=['GET', 'POST'])
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

@app.route('/count',methods=['GET','POST'])
def count():
    # リンク先のURLを表示するためにテンプレートに渡す
    link_params = request.args.get('id')
    if link_params is None:
        link_params = False
    post = Post.query.get(link_params)
    if link_params == False:
        return redirect('/')
    if not post:
        return redirect('/create?id=' + str(link_params))
    if request.method=='GET':
        return render_template('count.html',post=post)
    else:
        return redirect('/')
    
@app.route('/quick')
def quick():
    return render_template('quick.html')