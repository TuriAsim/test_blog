from datetime import datetime

from flask import Flask, render_template, request, session,redirect
from flask_sqlalchemy import SQLAlchemy
import json
import os

from werkzeug.utils import secure_filename

app=Flask(__name__)

with open('config.json','r') as c:
    params = json.load(c)["params"]
    print("params",params)


local_server=True
app.secret_key = 'super-secret-key'
app.config['UPLOAD_FOLDER']=params['upload_location']

# 'mysql://root:@localhost/coding_thender'
# "mysql+pymysql://root:@localhost/coding_thender"

if(local_server):
    app.config['SQLALCHEMY_DATABASE_URI'] = params['local_uri']
else:
    app.config['SQLALCHEMY_DATABASE_URI'] = params['prod_uri']
db = SQLAlchemy(app)

#contact table model
class Contacts(db.Model):
    # contact_id,name,email,phone_num,msg,date
    contact_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(20), unique=False, nullable=False)
    email = db.Column(db.String(12), unique=False, nullable=False)
    phone_num = db.Column(db.String(12), unique=False, nullable=False)
    msg = db.Column(db.String(100),  nullable=False)
    date = db.Column(db.String(12),  nullable=False)

#post table model
class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(80), nullable=False)
    slug = db.Column(db.String(21), nullable=False)
    content = db.Column(db.String(120), nullable=False)
    tagline=db.Column(db.String(50), nullable=False)
    post_img = db.Column(db.String(50), nullable=False)
    date = db.Column(db.String(12), nullable=True)

#login page
@app.route("/login",methods=['GET','POST'])
def login():
    if "user" in session and session['user'] == params['admin_user']:
        posts=Posts.query.all()
        return render_template("dashboard.html",params=params, posts=posts)
    if request.method == "POST":
        username=request.form.get("uname")
        password=request.form.get("pass")
        if username==params['admin_user'] and password==params['admin_password']:
            session['user']=username
            posts = Posts().query.all()
            return render_template("dashboard.html",params=params,posts=posts)
        # REDIRECT TO ADMIN PANEL
        pass
    else:
        return render_template("login.html", params=params)

#Logout page
@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/login')

#Delete post
@app.route("/delete/<string:sno>",methods=['GET','POST'])
def delete(sno):
    if "user" in session and session['user'] == params['admin_user']:
        post=Posts.query.filter_by(sno=sno).first()
        db.session.delete(post)
        db.session.commit()
    return redirect('/login')

#uploader page
@app.route("/uploader",methods=['GET','POST'])
def uploader():
    if "user" in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            f = request.files['myfile']
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
        return redirect('/login')


# edit page
@app.route("/edit/<string:sno>",methods=['GET','POST'])
def edit(sno):
    if "user" in session and session['user'] == params['admin_user']:
        if request.method == 'POST':
            box_title=request.form.get('title')
            slug = request.form.get('slug')
            content = request.form.get('content')
            tline = request.form.get('tline')
            img_file=request.form.get('img_file')
            date=datetime.now()
            print("post sno", sno)
            if sno == '0':
                post=Posts(title=box_title,slug=slug,content=content,tagline=tline,post_img=img_file,date=date)
                print("post inside",post)
                db.session.add(post)
                db.session.commit()
            else:
                post=Posts.query.filter_by(sno=sno).first()
                post.title=box_title
                post.slug=slug
                post.content=content
                post.tagline=tline
                post.img_file=img_file
                post.date=date
                db.session.commit()
                return redirect('/edit/'+sno)
        post=Posts.query.filter_by(sno=sno).first()
        print("post data",post)
        return render_template('edit.html',params=params,post=post,sno=sno)


#index page
@app.route("/")
def home():
    posts=Posts.query.filter_by().all()[0:params['no_of_posts']]
    return render_template('index.html',params=params,posts=posts);

#about page
@app.route("/about")
def about():
    return render_template('about.html',params=params);

#contact page
@app.route("/contact", methods=['GET', 'POST'])
def contact():
    if(request.method=='POST'):
        name=request.form.get('name')
        email=request.form.get('email')
        phone=request.form.get('phone')
        message=request.form.get('msg')
        entry=Contacts(name=name, email=email, phone_num=phone, msg=message, date=datetime.now())
        db.session.add(entry)
        db.session.commit()
    return  render_template('contact.html',params=params);

#post page
@app.route("/post/<string:post_slug>",methods=['GET'])
def post(post_slug):
    post_data=Posts.query.filter_by(slug=post_slug).first()
    return render_template('post.html',params=params,post_data=post_data)

if __name__ == "__main__":
    app.run(port=5001,debug=True);