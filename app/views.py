from flask import render_template, redirect, request, url_for, g, send_from_directory, flash, session, escape
from flask_login import current_user, login_required, login_user, logout_user
import os
from datetime import datetime
from app import app, db, login_manager
from .forms import LoginForm, SignupForm, CommentForm
from .models import User, Post, Comment


@app.route('/')
@app.route('/homepage')
@login_required
def homepage():
    title = 'Homepage'
    posts = Post.query.all()

    return render_template('homepage.html', title=title, posts=posts)



@login_manager.user_loader
def load_user(email):
    return User.query.filter_by(email=email).first()


@app.route('/login', methods=['GET', 'POST'])
def login():
    title = 'Login'
    if g.user is not None and g.user.is_authenticated:
        return redirect(url_for('homepage'))
    form = LoginForm()
    if request.method == 'POST':
        if form.validate_on_submit() and form.validate():

            user = User.query.filter_by(email=form.email.data.lower()).first()  # get data from DB and set it to a new session
            login_user(user, remember=form.remember_me.data)  # form.remember_me.data

            session['email'] = request.form['email']

            flash('Logged in successfully.')

            next = request.args.get('next')

            redirect_to_index = redirect(next or url_for('homepage'))
            return redirect_to_index
    return render_template('login.html', title=title, form=form)


@app.route('/signup', methods=['GET', 'POST'])
def register():
    form = SignupForm(request.form)
    print(form.validate())
    print(form.errors)
    if request.method == 'POST' and form.validate_on_submit() and form.validate():
        print('valid')
        user = User(form.email.data, form.password.data,
                    form.email.data[:form.email.data.index('@')])

        db.session.add(user)
        db.session.commit()

        return redirect(url_for('login'))

    return render_template('signup.html', title='Sign up', form=form)


@app.before_request
def before_request():
    g.user = current_user


@login_manager.user_loader
def load_user(id):
    return User.query.get(int(id))


@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('homepage'))


@app.errorhandler(404)
def not_found_error(error):
    title = 'Page not found'
    return render_template('404.html', title=title), 404


@app.route('/<post_id>', methods=['GET', 'POST'])
@login_required
def postpage(post_id):
    post = Post.query.filter_by(id=post_id).first()  # get post id here
    form = CommentForm()

    if request.method == 'POST' and form.validate_on_submit() and form.validate():

        comment = Comment(form.body.data, datetime.utcnow(), g.user.id, post_id)

        db.session.add(comment)
        db.session.commit()
    # get all comments; every comment has user_id --> use it to User.nickname TODO add filter by post_id:
    comments = Comment.query.filter(Comment.post_id.in_(post_id))
    # retrieve user ids from comments:
    user_ids = set(map(lambda c: c.user_id, comments))
    # get users by user ids of comments:
    users = User.query.filter(User.id.in_(user_ids)).all()  # get all user
    # create empty user comments list:
    user_comments = []
    # iterate over comments:
    for com in comments:
        # add each comment to key 'comment' and user of this comment (filtering by id) to key 'user':
        user_comments.append({"comment": com, "user": list(filter(lambda user: user.id == com.user_id, users)).pop()})
    return render_template('postpage.html', post=post, title=post.name, form=form, user_comments=user_comments)


@app.route('/delete_comment/<comment_id>', methods=['GET'])
def delete_comment(comment_id):
    comment = Comment.query.filter_by(id=comment_id).first()
    db.session.delete(comment)
    db.session.commit()
    return redirect(request.referrer)  # redirect user to the previous page


@app.route('/profile/<user_nickname>')
def profile_page(user_nickname):
    title = user_nickname
    # TODO ticket profile_page

    user = User.query.filter_by(nickname=user_nickname).first()
    comments = Comment.query.filter(Comment.user_id == user.id).all()
    posts = Post.query.filter(Post.id.in_([x.post_id for x in comments])).all()
    comment_post = []
    for com in comments:
        comment_post.append({'comment': com, 'post': list(filter(lambda post: post.id == com.post_id, posts))})

    return render_template('profilepage.html', title=title, user=user, comments=comments, posts=posts, comment_post=comment_post)


@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static/images'),
                               'favicon.ico')

