from flask import Flask, render_template, redirect, url_for
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField
from wtforms.validators import DataRequired, URL
from flask_ckeditor import CKEditor, CKEditorField
import datetime
import os

# Delete this code:
# import requests
# posts = requests.get("https://api.npoint.io/43644ec4f0013682fc0d").json()

app = Flask(__name__)
app.config['SECRET_KEY'] = os.getenv("KEY_SECRET")
ckeditor = CKEditor(app)
Bootstrap(app)

# CONNECT TO DB
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv("DATABASE_URL_1")
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


# CONFIGURE TABLE
class BlogPost(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(250), unique=True, nullable=False)
    subtitle = db.Column(db.String(250), nullable=False)
    date = db.Column(db.String(250), nullable=False)
    body = db.Column(db.Text, nullable=False)
    author = db.Column(db.String(250), nullable=False)
    img_url = db.Column(db.String(250), nullable=False)


with app.app_context():
    db.create_all()


# WTForm
class CreatePostForm(FlaskForm):
    title = StringField("Blog Post Title", validators=[DataRequired()])
    subtitle = StringField("Subtitle", validators=[DataRequired()])
    author = StringField("Your Name", validators=[DataRequired()])
    img_url = StringField("Blog Image URL", validators=[DataRequired(), URL()])
    body = CKEditorField("Blog Content", validators=[DataRequired()])
    submit = SubmitField("Submit Post")


@app.route('/')
def get_all_posts():
    posts = db.session.query(BlogPost).all()
    return render_template("index.html", all_posts=posts)


@app.route("/post/<int:post_id>")
def show_post(post_id):
    requested_post = BlogPost.query.get(post_id)
    return render_template("post.html", post=requested_post)


@app.route("/about")
def about():
    return render_template("about.html")


@app.route("/contact")
def contact():
    return render_template("contact.html")


@app.route("/delete/<post_id>")
def delete(post_id):
    post_to_delete = BlogPost.query.get(post_id)
    db.session.delete(post_to_delete)
    db.session.commit()
    return redirect(url_for("get_all_posts"))


@app.route("/edit-post/<post_id>", methods=["GET", "POst"])
def edit_post(post_id):
    post_to_edit = BlogPost.query.get(post_id)
    form = CreatePostForm(title=post_to_edit.title, subtitle=post_to_edit.subtitle,
                          img_url=post_to_edit.img_url, author=post_to_edit.author,
                          body=post_to_edit.body)
    if form.validate_on_submit():
        post_to_edit.title = form.title.data
        post_to_edit.subtitle = form.subtitle.data
        post_to_edit.author = form.author.data
        post_to_edit.img_url = form.img_url.data
        post_to_edit.body = form.body.data
        db.session.commit()
        return redirect(url_for('show_post', post_id=post_id))
    return render_template("make-post.html", title="Edit Post", post=post_to_edit, form=form)


@app.route("/new-post", methods=["GET", "POST"])
def new_post():
    form = CreatePostForm()
    now = datetime.date.today()
    date = now.strftime("%B %d,%Y")
    if form.validate_on_submit():
        new_record = BlogPost(date=date, title=form.title.data, subtitle=form.subtitle.data,
                              author=form.author.data, img_url=form.img_url.data, body=form.body.data)
        db.session.add(new_record)
        db.session.commit()
        return redirect(url_for('get_all_posts'))
    return render_template("make-post.html", title="New Post", form=form)


if __name__ == "__main__":
    app.run(debug=True)
    # host = '0.0.0.0', port = 5000