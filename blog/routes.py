from flask import Flask, render_template, url_for, request, redirect, flash
from blog import app, db
from blog.models import User, Post, Comment, Like, SavedPost
from blog.forms import RegistrationForm, LoginForm, CommentForm, LikeForm, UnlikeForm, SavedPostForm, ForgetPostForm
from flask_login import login_user, logout_user, login_required, current_user
from sqlalchemy import desc, asc

@app.route("/")
@app.route("/home")
def home():
    posts = Post.query.order_by(desc(Post.date)).limit(4).all()         # https://stackoverflow.com/questions/4582264/python-sqlalchemy-order-by-datetime
    return render_template('home.html', title='Home', posts=posts)

@app.route("/about")
def about():
    return render_template('about.html', title='About Us')

@app.route("/privacy")
def privacy():
    return render_template('privacy.html', title='Privacy Statement')

@app.route("/saved")
def saved():
    posts = Post.query.all()
    saved_posts = Post.query.filter(SavedPost.post_id.contains(Post.id) & SavedPost.author_id.contains(current_user.id)).all()
    return render_template('saved.html', title='About Us', posts=posts, saved_posts=saved_posts)

@app.route("/all")                                                      # All posts page
def all():
    posts = Post.query.order_by(desc(Post.date)).all()
    return render_template('all.html', title='All Posts', posts=posts)

@app.route("/ascending")                                                      # All posts ascending
def ascending():
    posts = Post.query.order_by(asc(Post.date)).all()
    return render_template('all.html', title='All Posts', posts=posts)

@app.route("/descending")                                                      # All posts descending
def descending():
    posts = Post.query.order_by(desc(Post.date)).all()
    return render_template('all.html', title='All Posts', posts=posts)

# @app.route("/admin")                # Comment this out if 
# def admin():                        # the admin panel keeps
#     return redirect('/admin')       # timing out

@app.route("/post/<int:post_id>")
def post(post_id):
    post = Post.query.get_or_404(post_id)
    comments = Comment.query.filter(Comment.post_id == post.id)
    form = CommentForm()
    like = LikeForm()
    unlike = UnlikeForm()
    save = SavedPostForm()
    forget = ForgetPostForm()
    if_liked = 0
    if_saved = 0
    if current_user.is_authenticated:
        if_liked = Like.query.filter(Like.post_id.contains(post_id) & Like.author_id.contains(current_user.id)).first()
        if_saved = SavedPost.query.filter(SavedPost.post_id.contains(post_id) & SavedPost.author_id.contains(current_user.id)).first()
    return render_template('post.html', title=post.title, post=post, comments=comments, form=form, like=like, unlike=unlike, if_liked=if_liked, save=save, forget=forget, if_saved=if_saved)

@app.route("/register", methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        user = User(firstname=form.firstname.data, surname=form.surname.data, username=form.username.data, email=form.email.data, password=form.password.data)
        db.session.add(user)
        db.session.commit()
        login_user(user)
        flash('Congratulations! You registered an account!')
        return redirect(url_for('home'))
    return render_template('register.html', title='Register', form=form)

@app.route("/login",methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user=User.query.filter_by(email=form.email.data).first()
        if user is not None and user.verify_password(form.password.data):
            login_user(user)
            flash('Congratulations! You logged in!')
            return redirect(url_for('home'))
        if user is not None and not user.verify_password(form.password.data):
            return redirect(url_for('login')), flash('INVALID EMAIL OR PASSWORD')
        if user is None:
            return redirect(url_for('login')), flash('INVALID EMAIL OR PASSWORD')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    flash('Congratulations! You have successfully logged out!')
    return redirect(url_for('home'))

@app.route('/post/<int:post_id>/comment', methods=['GET', 'POST'])
@login_required
def post_comment(post_id):
    post = Post.query.get_or_404(post_id)
    form = CommentForm()
    # like = LikeForm()
    if form.validate_on_submit():
        db.session.add(Comment(content=form.comment.data, post_id=post.id, author_id=current_user.id))
        db.session.commit()
        flash("Congratulations! You left a comment!")
        return redirect(f'/post/{post.id}')
    comments = Comment.query.filter(Comment.post_id == post.id)
    return render_template('post.html', post=post, comments=comments, form=form)

@app.route('/search')
@app.route('/post/search')
def search():
    query = request.args.get('q')
    # print(type(query))
    # print(hasattr(query,"len"))
    posts = []
    if query:
        posts = Post.query.filter(Post.title.contains(query) | Post.content.contains(query))
    if posts == None:
        return flash("'f{query}' returned no results.")
    return render_template("search.html", title="Search", posts=posts)

@app.route('/post/<int:post_id>/like', methods=['GET', 'POST'])
@login_required
def submit_like(post_id):
    post = Post.query.get_or_404(post_id)
    like = LikeForm()
    this_post = Like.query.filter(Like.post_id.contains(post_id) & Like.author_id.contains(current_user.id)).first()
    if like.is_submitted():
        if not this_post:
            db.session.add(Like(post_id=post.id, author_id=current_user.id))
            db.session.commit()
            flash('Congratulations! You liked this post!')
            return redirect(f'/post/{post.id}')
        flash('Commiserations! You have already liked this post!')
    return render_template('post.html', post=post, like=like)

@app.route('/post/<int:post_id>/unlike', methods=['GET', 'POST'])
@login_required
def submit_unlike(post_id):
    post = Post.query.get_or_404(post_id)
    unlike = UnlikeForm()
    remove_like = Like.query.filter(Like.post_id.contains(post_id) & Like.author_id.contains(current_user.id)).first()
    if unlike.is_submitted():
        if remove_like:
            db.session.delete(remove_like)
            db.session.commit()
            flash('Congratulations! You unliked this post!')
            return redirect(f'/post/{post.id}')
        flash('Commiserations! You have not liked this post yet!')
    return render_template('post.html', post=post, unlike=unlike)

@app.route('/post/<int:post_id>/saved', methods=['GET', 'POST'])
@login_required
def save_this(post_id):
    post = Post.query.get_or_404(post_id)
    save = SavedPostForm()
    save_post = SavedPost.query.filter(SavedPost.post_id.contains(post_id) & SavedPost.author_id.contains(current_user.id)).first()
    if save.is_submitted():
        if not save_post:
            print(save_post)
            db.session.add(SavedPost(post_id=post.id, author_id=current_user.id))
            db.session.commit()
            flash('Congratulations! You saved this post!')
            return redirect(f'/post/{post.id}')
        flash('Commiserations! You have already saved this post!')
    return render_template('post.html', post=post, save=save)

@app.route('/post/<int:post_id>/forget', methods=['GET', 'POST'])
@login_required
def submit_unsave(post_id):
    post = Post.query.get_or_404(post_id)
    forget = ForgetPostForm()
    remove_save = SavedPost.query.filter(SavedPost.post_id.contains(post_id) & SavedPost.author_id.contains(current_user.id)).first()
    if forget.is_submitted():
        if remove_save:
            db.session.delete(remove_save)
            db.session.commit()
            flash('Congratulations! You unsaved this post!')
            return redirect(f'/post/{post.id}')
        flash('Commiserations! You have not saved this post yet!')
    return render_template('post.html', post=post, forget=forget)



# @app.route('/post/<int:post_id>/like', methods=['GET', 'POST'])
# @login_required
# def submit_like(post_id):
#     post = Post.query.get_or_404(post_id)
#     like = LikeForm()
#     #this_post = Like.query.filter_by(post_id).all()
#     this_post = Like.query.filter(post_id).all()
#     is_user = this_post.author_id == current_user.id
#     if like.is_submitted() and is_user == False:
#         db.session.add(Like(post_id=post.id, author_id=current_user.id))
#         db.session.commit()
#         flash('Thanks for liking')
#         return redirect(f'/post/{post.id}')

#     return render_template('post.html', post=post, like=like)