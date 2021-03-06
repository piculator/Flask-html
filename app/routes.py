from flask import render_template, flash, redirect, url_for, request
from app import app, db
from app.forms import LoginForm, RegistrationForm, EditProfileForm, EditSecurityForm
from app.forms import check_user
from flask_login import current_user, login_user, login_required, logout_user
from app.models import User
from werkzeug.urls import url_parse
from datetime import datetime

# 定义一个进制转换函数
def byte_trans(x):
    byte_name=('','K','M','G','T','P')
    i=0
    while not x//1024==0:
        i+=1
        x/=1024
    if i>5:
        return '>1024 PB'
    elif i==0:
        return str(x)+' B'
    else:
        return '%.2f' % x+' '+byte_name[i]+'B'

# 记录用户上次访问的时间
@app.before_request
def before_request():
    if current_user.is_authenticated:
        current_user.last_seen = datetime.utcnow()
        db.session.commit()

@app.route('/')
@app.route('/index')
@login_required
def index():
    print(current_user)
    return render_template('index.html', title='图形计算器主页')

@app.route('/login', methods=['GET', 'POST'])
def login():
    # 已登录的用户访问登录页，则弹回主界面
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = LoginForm()
    # 验证是否来自客户端：
    if form.is_from_client.data:
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            return {"is_logged_in":False, "reason":"无效的用户名"}
        elif not user.check_password(form.password.data):
            return {"is_logged_in":False, "reason":"密码错误，请重新输入"}
        else:
            return {"is_logged_in":True}
    # 来自网页的表单提交
    elif form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user is None:
            flash('无效的用户名')
            return redirect(url_for('login'))
        elif not user.check_password(form.password.data):
            flash('密码错误，请重新输入')
            return redirect(url_for('login'))
        else:
            login_user(user, remember=form.remember_me.data)
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                next_page = url_for('index')
            return redirect(next_page)
    return render_template('login.html', title='用户登录', form=form)

@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('index'))

@app.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    form = RegistrationForm()

    if form.is_from_client.data:
        # 检验表单是否有空项
        if not (form.username.data and form.password.data and form.identity.data):
            return {
                "is_registered": False,
                "message": "表单信息不完整，请检查后再提交！",
            } 
        else:
            # 检验用户名是否符合格式
            if not check_user(form.username.data):
                return {
                    "is_registered": False,
                    "message": "用户名格式错误"}
            else:
                # 检验用户名是否已经注册
                user = User.query.filter_by(username=form.username.data).first()
                if user is not None:
                    return {
                        "is_registered": False,
                        "message": "用户名已被使用，请换一个用户名"}
                else:
                    user = User(username=form.username.data)
                    user.set_password(form.password.data)
                    user.identity = form.identity.data
                    db.session.add(user)
                    db.session.commit()
                    return {
                        "is_registered":True,
                        "message":"恭喜，您已经成功注册Piculator会员！"}
    
    elif form.validate_on_submit():
        user = User(username=form.username.data)
        user.set_password(form.password.data)
        user.identity = form.identity.data
        db.session.add(user)
        db.session.commit()
        flash('恭喜，您已经成功注册Piculator会员！')
        return redirect(url_for('login'))
    return render_template('register.html', title='用户注册', form=form)

@app.route('/service_item')
def service_item():
    return render_template('service_item.html')

@app.route('/user/<username>')
@login_required
def user(username):
    user = User.query.filter_by(username=username).first_or_404()
    if user.cloud_storage:
        cloud_storage = byte_trans(int(user.cloud_storage))
        cs_percent = '%.2f' % (user.CloudStorage / 104857.6)
    else:
        cloud_storage = cs_percent = 0
    # posts = [
    #     {'author': user, 'body': 'Test post #1'},
    #     {'author': user, 'body': 'Test post #2'}
    # ]
    return render_template('user.html', user=user, 
    cs=cloud_storage, 
    cspercent=cs_percent)

# 编辑个人信息
@app.route('/edit_profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm(current_user.username)
    if form.validate_on_submit():
        current_user.username = form.username.data
        current_user.gender = form.gender.data
        current_user.about_me = form.about_me.data
        db.session.commit()
        flash('您的设置已经保存')
        return redirect(url_for('edit_profile'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', title='编辑个人信息',
                           form=form)

# 账户安全
@app.route('/security/<username>')
@login_required
def account_security(username):
    # 检测当前用户是否为注册用户
    if not current_user.username == username:
        return '提示：非法访问！'
    else:
        email = current_user.email
        si = current_user.secret_insurance_question

        return render_template('account_security.html', title='账户安全',
        email=email, si=si)

@app.route('/edit_security')
@login_required
def edit_security():
    form = EditSecurityForm(current_user.username)
    if form.validate_on_submit():
        current_user.email = form.email.data
        current_user.secret_insurance_question = form.secret_insurance_question.data
        current_user.secret_insurance_answer = form.about_me.data
        db.session.commit()
        flash('您的设置已经保存')
        return redirect(url_for('edit_security'))
    return render_template('edit_security.html', title='编辑邮箱和密保',
                        form=form)