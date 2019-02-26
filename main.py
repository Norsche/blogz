from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:blogz@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'secretkey'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120))
    content = db.Column(db.String(1024))
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, name, content, owner):
        self.name = name
        self.content = content
        self.owner = owner


class User(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(120), unique=True)
    password = db.Column(db.String(120))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, email, password):
        self.email = email
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'index']
    if request.endpoint not in allowed_routes and 'email' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        user = User.query.filter_by(email=email).first()
        

        if user and user.password == password:
            session['email'] = email
            flash("Logged in")
            print(session)
            return redirect('/newpost')
        else:
            flash('User password incorrect, or user does not exist', 'error')

    return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():

    password_error = ''
    verify_error = ''
    email_error = ''
    email = ''
    password = ''
    verify = ''

    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']
        verify = request.form['verify']
        email = request.form['email']
        password_error = ''
        verify_error = ''
        email_error = ''

        if password == '':
            password_error = "Please enter a valid password."
            password = ''

        for character in password:
            if character == ' ':
                password_error = "Please enter a valid password wth no spaces."

        if verify == '':
            verify_error = "Plese enter a valid password confirmation."
            verify = ''

        if len(password) < 3 or len(password) > 20:
            password_error = "Please enter a password between 3 and 20 characters."
            password = ''

        if password != verify:
            verify_error = "Passwords do not match."
            verify = ''

        if len(email) < 3 or len(email) > 20:
            email_error = "Please enter an email between 3 and 20 characets."
        
        for character in email:
            if character == '':
                email_error = "Please enter a valid email address."

        count = 0
        for character in email:
            if character == '@':
                count += 1
        
        if count > 1 or count == 0:
            email_error = "Please enter a valid email address"
        
        count = 0
        for character in email:
            if character == '.':
                count += 1

        if count > 1 or count == 0:
            email_error = "Pleaes enter a valid email address."

        if email == '':
            email_error = 'Please enter a valid email address.'

        # TODO - validate user's data

        if not password_error and not verify_error and not email_error:
            existing_user = User.query.filter_by(email=email).first()
            if not existing_user:
                new_user = User(email, password)
                db.session.add(new_user)
                db.session.commit()
                session['email'] = email
                return redirect('/newpost')

            else:
                # TODO - user better response messaging
                return "<h1>Duplicate user</h1>"

        else:
            return render_template('signup.html', password_error=password_error, verify_error = verify_error, email_error = email_error, password='', verify='', email=email)

    else:
        return render_template('signup.html', password_error=password_error, verify_error = verify_error, email_error = email_error, password='', verify='', email=email)

@app.route('/logout')
def logout():
    del session['email']
    return redirect('/blog')

@app.route('/blog')
def blog():
    posts = Blog.query.all()
    blog_id = request.args.get('id')
    user_id = request.args.get('user')
    
    if user_id:
        posts = Blog.query.filter_by(owner_id=user_id)
        return render_template('user.html', posts=posts, header="User Posts")
    if blog_id:
        post = Blog.query.get(blog_id)
        return render_template('entry.html', post=post )

    return render_template('blog.html', posts=posts, header='All Blog Posts')

@app.route('/', methods=['POST', 'GET'])
def index():

    users = User.query.all()
    return render_template('index.html', title="Blogz!", users=users)



@app.route('/newpost', methods=['POST', 'GET'])
def newpost():

    owner = User.query.filter_by(email=session['email']).first()

    if request.method == 'POST':
        post_title = request.form['new-post-title']
        post_content = request.form['new-post']
        title_error = ''
        content_error = ''

        if post_title == '':
            title_error = 'Please fill in the title.'

        if post_content == '':
            content_error = 'Please fill in the content.'
        
        if not title_error and not content_error:
            new_post = Blog(post_title, post_content, owner)
            db.session.add(new_post)
            db.session.commit()
            return redirect('/blog?id='+str(new_post.id))
        else:
            return render_template('newpost.html', title_error=title_error, content_error=content_error, post_title=post_title, post_content=post_content)

    return render_template('newpost.html', title="Make a new blog post")



#@app.route('/delete-post', methods=['POST'])
#def delete_post():

 #   post_id = int(request.form['post-id'])
  #  post = Post.query.get(post_id)
   # db.session.add(post)
    #db.session.commit()

    #return redirect('/')


if __name__ == '__main__':
    app.run()