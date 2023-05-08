from io import BytesIO

from flask import Blueprint, render_template, request, redirect, url_for, jsonify, session, make_response
from flask_login import login_user, logout_user, login_required, current_user
from models import db
from models.user import User
from captcha.image import ImageCaptcha  # pip install captcha
import numpy as np
import matplotlib.pyplot as plt
from PIL import Image
import random

# 验证码中的字符, 就不用汉字了
number = ['0', '1', '2', '3', '4', '5', '6', '7', '8', '9']
alphabet = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h', 'i', 'j', 'k', 'l', 'm', 'n', 'o', 'p', 'q', 'r', 's', 't', 'u',
            'v', 'w', 'x', 'y', 'z']
ALPHABET = ['A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
            'V', 'W', 'X', 'Y', 'Z']


# 验证码一般都无视大小写；验证码长度4个字符
def random_captcha_text(char_set=number + alphabet + ALPHABET, captcha_size=4):
    captcha_text = []
    for i in range(captcha_size):
        c = random.choice(char_set)
        captcha_text.append(c)
    return captcha_text


# 生成字符对应的验证码
def gen_captcha_text_and_image():
    image = ImageCaptcha()

    captcha_text = random_captcha_text()
    captcha_text = ''.join(captcha_text)

    captcha = image.generate(captcha_text)
    # image.write(captcha_text, captcha_text + '.jpg')  # 写到文件

    return captcha_text, captcha


auth = Blueprint('auth', __name__)


@auth.route('/captcha')
def captcha():
    text, img = gen_captcha_text_and_image()
    session['captcha'] = text
    response = make_response(img.read())
    response.headers['Content-Type'] = 'image/png'
    return response


@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'GET':
        return render_template('login.html')
    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        data = request.get_json()
        name = data.get('username')
        password = data.get('password')
        user_captcha = data.get('captcha')
        if 'captcha' not in session or session['captcha'] != user_captcha.lower():
            return jsonify({'success': False, 'message': '验证码错误'})
        session.pop('captcha', None)
        user = User.query.filter_by(name=name).first()
        if user is not None and user.check_password(password):
            login_user(user)
            return jsonify({'success': True})
        else:
            return jsonify({'success': False, 'message': 'Invalid username or password'})


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login.html'))


@auth.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'GET':
        return render_template('register.html')

    if current_user.is_authenticated:
        return redirect(url_for('index'))

    if request.method == 'POST':
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')

        if User.query.filter_by(name=name).first() is not None:
            print('Username is already taken')
            return jsonify({'success': False, 'message': 'Username is already taken'})
        elif User.query.filter_by(email=email).first() is not None:
            print('Email is already registered')
            return jsonify({'success': False, 'message': 'Email is already registered'})
        else:
            user = User(name=name, email=email)
            user.set_password(password)
            db.session.add(user)
            db.session.commit()
            return jsonify({'success': True, 'message': 'Registration successful. Please log in.'})
