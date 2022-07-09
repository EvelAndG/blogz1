from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:geveland12@localhost:3306/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = '123456789'


class Blog(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.String(500))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self,title,body,owner):
        self.title = title
        self.body = body 
        self.owner = owner


class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True)
    password = db.Column(db.String(20))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password


@app.route('/', methods=['POST', 'GET'])
def index():
    users = User.query.all()
    return render_template('index.html', users=users)


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if "user" in request.args:
        user_id = request.args.get("user")
        user = User.query.get(user_id)
        user_blogs = Blog.query.filter_by(owner=user).all()
        return render_template("singleUser.html", page_title = user.username + "'s Posts", user_blogs=user_blogs)

    single_post = request.args.get("id")
    if single_post:
        blog = Blog.query.get(single_post)
        return render_template("viewpost.html", blog=blog)

    else:
        blogs = Blog.query.all()
        return render_template("blog.html", page_title="All blog posts", blogs=blogs)


@app.route('/newpost', methods=['POST', 'GET'])
def new_blog_post():

    if request.method == 'GET':
        return render_template('newpost.html')
    
    if request.method =='POST':
        title_entry = request.form['title']
        body_entry = request.form['body']

        title_error = ''
        body_error = ''

        if len(title_entry) == 0:
            flash("Your blog needs a title")
            return redirect("/newpost")
        if len(body_entry) == 0:
            flash("Your blog needs a body")
            return redirect("/newpost")
        if title_error or body_error:
            return render_template('newpost.html')
        
        else:
            if len(title_entry) and len(body_entry) > 0:
                owner = User.query.filter_by(username=session['username']).first()
                new_entry = Blog(title_entry, body_entry, owner)
                db.session.add(new_entry)
                db.session.commit()
                return redirect("/blog?id=" + str(new_entry.id))

#Needs checked
@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'GET':
        return render_template('signup.html')

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']

        if len(username) < 3 or len(username) > 20:
            flash ("Invalid User Name")
            return redirect("/signup")
        if len(password) < 3 or len(password) > 20:
            flash ("Invalid Password")
            return redirect("/signup")
        if password != verify:
            ##
            flash("Passwords do not match")
            return redirect("/signup")
        
        existing_user = User.query.filter_by(username=username).first()
        if existing_user:
            return "<h2>That User Name already exists"
        if not existing_user:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username']=username
            return redirect('/newpost')
        else:
            return render_template ('signup.html')


@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username']=username
            flash("logged in")
            return redirect('/newpost')
        else:
            flash("Your username or password is incorrect")
            return redirect('/login')

    return render_template('login.html')


@app.route('/logout',methods=['POST', 'GET'])
def logout():
    del session['username']
    return redirect('/')



@app.before_request
def require_login():
    allowed_routes = ['login','signup']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect ('/login')

if __name__ == '__main__':
    app.run()