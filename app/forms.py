from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, TextAreaField, RadioField, SelectField
from wtforms.validators import ValidationError, DataRequired, Email, EqualTo, Length
from app.models import User

class LoginForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    password = PasswordField('密码', validators=[DataRequired()])
    remember_me = BooleanField('记住我')
    submit = SubmitField('点此登录')

class RegistrationForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    # email = StringField('邮箱', validators=[DataRequired(), Email()])
    password = PasswordField('密码', validators=[DataRequired()])
    password2 = PasswordField(
        '确认密码', validators=[DataRequired(), EqualTo('password')])
    identity = RadioField('您的身份是', choices=[
        ('S','学生'),('T','教师'),('O','其他')
    ], validators=[DataRequired()])
    accept = BooleanField('我同意服务条款', validators=[DataRequired()])
    submit = SubmitField('点此注册')

    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()
        if user is not None:
            raise ValidationError('用户名已被使用，请换一个用户名')
    
    # def validate_accept(self, accept):
    #     if accept:
    #         raise ValidationError('须同意服务条款才可注册')

    # def validate_email(self, email):
    #     user = User.query.filter_by(email=email.data).first()
    #     if user is not None:
    #         raise ValidationError('邮箱已被注册')

class EditProfileForm(FlaskForm):
    username = StringField('用户名', validators=[DataRequired()])
    gender = RadioField('性别', choices=[
        ('M','男'),('F','女'),('S','保密')
    ], validators=[DataRequired()]) #M,F,S for male,female,secret
    about_me = TextAreaField('个人简介', validators=[Length(min=0, max=140)])
    submit = SubmitField('提交')

    def __init__(self, original_username, *args, **kwargs):
        super(EditProfileForm, self).__init__(*args, **kwargs)
        self.original_username = original_username

    def validate_username(self, username):
        if username.data != self.original_username:
            user = User.query.filter_by(username=self.username.data).first()
            if user is not None:
                raise ValidationError('此用户名已被使用')
