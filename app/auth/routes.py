from flask import render_template, redirect, url_for, flash, request, current_app
from werkzeug.urls import url_parse
from flask_login import login_user, logout_user, current_user, login_required
from app import db
from app.auth import bp
from app.auth.forms import LoginForm, RegistrationForm, \
    ResetPasswordRequestForm, ResetPasswordForm
from app.models import User
from app.auth.email import send_password_reset_email, send_registry_confirm_email
from app.auth import services


@bp.route('/login', methods=['GET', 'POST'])
def login():
    current_app.logger.info('request login')
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user is None or not user.check_password(form.password.data):
            flash('用户名或者密码无效')
            return redirect(url_for('auth.login'))
        if not user.is_active:
            flash('请激活后再登录！')
            return redirect(url_for('auth.login'))
        login_user(user, remember=form.remember_me.data)
        current_app.logger.info('User: %s was login' % user.username)
        next_page = request.args.get('next')
        if not next_page or url_parse(next_page).netloc != '':
            next_page = url_for('main.index')
        return redirect(next_page)
    return render_template('auth/login.html', title='登录', form=form)


@bp.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('main.index'))


@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(email=form.email.data)
        user.set_password(form.password.data)
        db.session.add(user)
        db.session.flush()
        send_registry_confirm_email(user)
        db.session.commit()
        flash('请前往您的邮箱确认注册！')
        return redirect(url_for('auth.login'))
    return render_template('auth/register.html', title='注册', form=form)


@bp.route('/reset_password_request', methods=['GET', 'POST'])
def reset_password_request():
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    form = ResetPasswordRequestForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user:
            send_password_reset_email(user)
        flash('请前往您的邮箱获得重置密码信息')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password_request.html', title='重置密码', form=form)


@bp.route('/reset_password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_reset_password_token(token)
    if not user:
        return redirect(url_for('main.index'))
    form = ResetPasswordForm()
    if form.validate_on_submit():
        user.set_password(form.password.data)
        flash('密码重置成功')
        return redirect(url_for('auth.login'))
    return render_template('auth/reset_password.html', form=form)


@bp.route('/register_confirm/<token>')
def register_confirm(token):
    if current_user.is_authenticated:
        return redirect(url_for('main.index'))
    user = User.verify_register_confirm_token(token)
    if not user:
        return redirect(url_for('main.index'))
    user.activate()
    if user.email in current_app.config['ADMINS']:
        services.set_user_role(user, 'super')
    else:
        services.set_default_permission(user)
    flash('用户已激活，请登录。')
    return redirect(url_for('auth.login'))


@bp.route('/active_user/<int:user_id>')
@login_required
def active_user(user_id):
    role = current_user.roles.filter_by(role='ADMIN').first()
    if role:
        user = User.query.filter_by(id=user_id).first()
        user.active = True
        db.session.commit()
    else:
        flash('此功能只有管理员有权限')
    return redirect(url_for('main.index'))


@bp.route('/user_management')
@login_required
def user_manager():
    users = User.query.all()
    return render_template("user_management.html", users=users)
