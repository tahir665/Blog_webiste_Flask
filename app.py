from flask import Flask, render_template,request,redirect,session
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from flask_mail import Mail,Message
import json
import os
from werkzeug.utils import secure_filename
local_server=True
with open("config.json","r") as c:
    params=json.load(c)["params"]

app = Flask(__name__)

app.secret_key="supersecretkey"

app.config['UPLOAD_FOLDER']=params["uploader_path"]
app.config['MAIL_SERVER']='sandbox.smtp.mailtrap.io'
app.config['MAIL_PORT'] = 2525
app.config['MAIL_USERNAME'] = '3f435a540d408b'
app.config['MAIL_PASSWORD'] = '969cb103e6bda8'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

mail = Mail(app)


if (local_server):
    app.config["SQLALCHEMY_DATABASE_URI"] = params["local_uri"]
else:
    app.config["SQLALCHEMY_DATABASE_URI"] = params["prod_uri"]
db = SQLAlchemy(app)




#contact class for database
class Contacts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(10), nullable=False)
    email = db.Column(db.String(15), nullable=False)
    phone = db.Column(db.String(13), nullable=False)
    msg = db.Column(db.String(120), nullable=False)
    date = db.Column(db.DateTime(15),default=datetime.now(), nullable=True)

#posts class for database
class Posts(db.Model):
    sno = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    slug = db.Column(db.String(150), nullable=False)
    content = db.Column(db.String(150), nullable=False)
    img = db.Column(db.String(25), nullable=False)
    date = db.Column(db.String(15),default=datetime.now(), nullable=True)
    


@app.route("/")
def home():
    # posts=Posts.query.filter_by().all()
    
    # posts=Posts.query.order_by(Posts.sno.desc())[0:3]
    # page=request.args.get("number")
    # if(str(page).isnumeric()):
    #     page=0
    
    # #first
    # if page==1:
    #     previous="#"    
    #     next="/?number="+str(page+1)
    # elif(page==last):
    #     next="#"    
    #     previous="/?number="+str(page-1)
    # else:
    #     previous="/?number="+str(page-1)
    #     next="/?number="+str(page+1)






    
    # posts=Posts.query.filter_by().all()[0:3]
    posts=Posts.query.order_by(Posts.sno.desc())[0:3]


    return render_template('index.html',params=params,posts=posts)


@app.route("/about")
def about():
    return render_template('about.html',params=params)


@app.route("/contact", methods=['GET','POST'])
def contact():
    if (request.method=='POST'):
        name=request.form.get('name')
        email=request.form.get('email')
        phone=request.form.get('phone')
        message=request.form.get('message')
        
        entry=Contacts(name=name,email=email,msg=message,phone=phone,date=datetime.now())
        db.session.add(entry)
        db.session.commit()

        msg = Message('Mail Received from '+name, sender =   email, recipients = ['m.tahee786@gmail.com'])
        msg.body = message+"\n" + phone
        mail.send(msg)
    return render_template('contact.html',params=params)

@app.route("/post/<string:post_slug>", methods=['GET'])
def blog_post(post_slug):

    post=Posts.query.filter_by(slug=post_slug).first()


    return render_template('post.html',params=params,post=post)


@app.route("/login",methods=['GET','POST'])
def login_page():
    if 'user' in session and session['user']==params['admin_user']:
        posts=Posts.query.all()
        
        return render_template("dashboard.html",params=params,posts=posts)

    if request.method=='POST':
        username=request.form['uname']
        password=request.form['pass']
        if username==params['admin_user'] and password==params['admin_password']:
            session['user']=username
            posts=Posts.query.all()
            return render_template("dashboard.html",params=params,posts=posts)
        else: 
            return redirect('/login')
               
    else:
        return render_template('login.html',params=params)

@app.route("/edit/<string:sno>",methods=['GET','POST'])
def edit(sno):
    print(sno)
    print("123234234")
    if 'user' in session and session['user']==params['admin_user']:
        if request.method=='POST':
            box_title=request.form.get('title')
            slug=request.form.get('slug')
            content=request.form.get('content')
            img=request.form.get('img_file')

            if sno=="0":
                post=Posts(title=box_title,slug=slug,content=content,img=img,date=datetime.now())
                db.session.add(post)
                db.session.commit()
            else:
                post=Posts.query.filter_by(sno=sno).first()
                post.title=box_title
                post.slug=slug
                post.content=content
                post.img=img
                db.session.commit()

    post=Posts.query.filter_by(sno=sno).first()   
    return render_template('edit.html',params=params,post=post,sno=sno)       

@app.route("/delete/<string:sno>",methods=['GET','POST'])
def delete(sno):
    if "user" in session and session['user']==params['admin_user']:
        post=Posts.query.filter_by(sno=sno).delete()
        db.session.commit()

        return redirect('/login')  


@app.route("/upload",methods=['GET','POST'])
def uploader():
    if "user" in session and session['user']==params['admin_user']:
        if request.method=='POST':
            print("file uploaded")
            f = request.files['myfile']  
            f.save(os.path.join(app.config['UPLOAD_FOLDER'], secure_filename(f.filename)))
            return "Uploaded successfully!"
    
@app.route("/logout")
def logout():
    session.pop('user')
    return redirect('/login')       



app.run(debug=True)

