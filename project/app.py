from flask import Flask, render_template, url_for, request, redirect, flash, session, g
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

# libraries for Flask-WTForms
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField
from wtforms.validators import InputRequired, Email, Length, EqualTo

# generate & check hashed password
from werkzeug.security import generate_password_hash, check_password_hash

# 
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user

app = Flask(__name__)
# app.config['SECRET_KEY'] = 'thisisverysecretive!'

Bootstrap(app)

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


####----------- START OF DATABASES --------------###
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///test.db'
# app.config['SQLALCHEMY_BINDS'] = {
#     'dtMovies':     'sqlite:///dtMovies.db',
#     'userMovies':   'sqlite:///userMovies.db'
#     }

# env/source/activate 

# run python in the terminal, then
# from app import db 
# db.create_all(bind='movies')

db = SQLAlchemy(app)



class userTest(UserMixin, db.Model):
    __tablename__ = 'userTest'
    # __table_args__ = {'schema': 'userTest'}
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(200))
    movies = db.relationship('userMovies', backref='userTest')

    def __repr__(self):
        return '<User %r>' % self.id

class dtMovies(db.Model):
    __tablename__ = 'dtMovies'
    # __table_args__ = {'schema': 'dtMovies'}
    # __bind_key__ = 'dtMovies' # bind the movies database
    id = db.Column(db.Integer, primary_key=True)
    director_name = db.Column(db.String(200))
    duration = db.Column(db.String(200))
    actor_2_name = db.Column(db.String(200))
    genres = db.Column(db.String(200))
    actor_1_name = db.Column(db.String(200))
    movie_title = db.Column(db.String(200))
    actor_3_name = db.Column(db.String(200))
    plot_keywords = db.Column(db.String(200))
    movie_imdb_link = db.Column(db.String(200))
    language = db.Column(db.String(200))
    country = db.Column(db.String(200))
    content_rating = db.Column(db.String(200))
    title_year = db.Column(db.String(200))
    imdb_score = db.Column(db.String(200))
    user = db.relationship('userMovies',backref='dtMovies')
    # date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<dtMovies %r>' % self.id  

class userMovies(db.Model):
    __tablename__ = 'userMovies'
    # __table_args__ = {'schema': 'userMovies'}
    # __bind_key__ = 'userMovies'
    id = db.Column(db.Integer, primary_key=True)
    uid = db.Column(db.Integer, db.ForeignKey('userTest.id'))
    mid = db.Column(db.Integer, db.ForeignKey('dtMovies.id'))
    score = db.Column(db.Integer)
    review = db.Column(db.String(1000))
    date_created = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return '<userMovies %r>' % self.id

        

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired()])
    password = PasswordField('password', validators=[InputRequired()])
    remember = BooleanField('remember me')

class RegistrationForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80), EqualTo('confirm', message='Password must match')])
    confirm = PasswordField('repeat password')

@login_manager.user_loader
def load_user(user_id):
    return userTest.query.get(int(user_id))




####----------- END OF DATABASES --------------###


@app.route('/', methods=['POST', "GET"])
def index():
    form = LoginForm()
    if form.validate_on_submit():
        user = userTest.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user,remember=form.remember.data)
                session['logged_in'] = True
                flash('Logged in successfully.')
                return redirect('/dashboard')
        flash('Invalid usernanme or password')
        
    return render_template('index.html', form=form)


@app.route('/login/', methods=['GET', 'POST'])
def login():
    # if session['logged_in']:
    #     return redirect('/dashboard')
    form = LoginForm()
    if form.validate_on_submit():
        user = userTest.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user,remember=form.remember.data)
                session['logged_in'] = True
                flash('Logged in successfully.')
                return redirect('/dashboard')
        flash('Invalid usernanme or password')

    return render_template('login.html', form=form)

@app.route('/signup', methods=["GET", "POST"])
def signup():
    form = RegistrationForm()

    if form.validate_on_submit():

        if db.session.query(userTest).filter_by(username=form.username.data).count() >= 1:
            flash("The username has been taken, try another one.")
        
        elif db.session.query(userTest).filter_by(email=form.email.data).count() >= 1:
            flash("The email has been used, try another one.")

        else:
            hashed_password = generate_password_hash(form.password.data, method='sha256')
            new_user = userTest(username=form.username.data, email=form.email.data, password=hashed_password)

            try:
                db.session.add(new_user)
                db.session.commit()

                flash('New user has been created')
                return redirect('/')
            except:
                flash("unknown error, please try again.")

    return render_template('signup.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    uid = current_user.get_id()

    # userComments = db.session.query(userMovies, dtMovies).outerjoin(dtMovies, userMovies.mid == dtMovies.id).all()

    recent = db.session.query(userMovies, dtMovies).filter_by(uid=uid).outerjoin(dtMovies, userMovies.mid == dtMovies.id).order_by(userMovies.date_created.desc()).all()

    # print(recent[1][0].uid)
    # print(userComments2[1])


    # for uc in userComments2:
    #     print(uc[1].movie_title)

    # r = userComments.query.filter_by(userComments[0].id=uid).order_by(userComments[1].date_created.desc()).all()
    # print(r)
    # recent = userMovies.query.filter_by(uid=uid).order_by(userMovies.date_created.desc()).all()
    return render_template('dashboard.html', name=current_user.username, recent=recent)


@app.route('/logout')
@login_required
def logout():
    logout_user()
    session['logged_in'] = False
    return redirect('/')



@app.route('/add_movies', methods=['GET', 'POST'])
# @app.route('/add_movies/', methods=['GET', 'POST'])
@login_required
def add_new():
    if request.method == 'POST':

        movie_title = request.form['movie_title']
        title_year = request.form['title_year']
        country = request.form['country']
        duration = request.form['duration']
        director_name = request.form['director_name']
        actor_1_name = request.form['actor_1_name']
        actor_2_name = request.form['actor_2_name']
        actor_3_name = request.form['actor_3_name']
        genres = request.form['genres']
        language = request.form['language']
        content_rating = request.form['content_rating']
        movie_imdb_link = request.form['movie_imdb_link']
        imdb_score = request.form['imdb_score']

        new_movie = dtMovies(
            movie_title=movie_title,
            title_year=title_year,
            country=country,
            duration=duration,
            director_name=director_name,
            actor_1_name=actor_1_name,
            actor_2_name=actor_2_name,
            actor_3_name=actor_3_name,
            genres=genres,
            language=language,
            content_rating=content_rating,
            movie_imdb_link=movie_imdb_link,
            imdb_score=imdb_score
        )
        print('new movie')
        print(movie_title)
        print(new_movie)
        
        try:
            db.session.add(new_movie)
            db.session.commit()

            flash("the movie has been added.")

            return redirect('/datatable')

        except: 

            flash('Theres an error adding your movie')
            
    return render_template('add_movies.html')

@app.route('/movies', methods=['GET', 'POST'])
@app.route('/movies/', methods=['GET', 'POST'])
def movies():

    mid = request.args.get('id')
    movie = dtMovies.query.get_or_404(mid)
    # comments = userMovies.query.filter_by(mid=mid).order_by(userMovies.date_created).all()
    userComments = db.session.query(userTest, userMovies).outerjoin(userMovies, userTest.id == userMovies.uid).all()

    watched = 0

    if session['logged_in']:
        uid = current_user.get_id()

        if db.session.query(userMovies).filter_by(mid=mid,uid=uid).count() >= 1:
            watched = 1

        if request.method == 'POST':

            if watched == 0: 
                score = request.form['score']
                review = request.form['review']
                newItem = userMovies(uid=uid,mid=mid,score=score,review=review)
                try:
                    db.session.add(newItem)
                    db.session.commit()
                    flash('your review is added')
                    return redirect(request.url)

                except:
                    flash("there is an error adding your review")
            else: 
                flash("Your review was already added")
        
        return render_template('movies.html', movie=movie, uid=uid, watched=watched, userComments=userComments)
    else:
        return render_template('movies.html', movie=movie, userComments=userComments)


@app.route('/usr', methods=['GET', 'POST'])
@app.route('/usr/<int:uid>', methods=['GET', 'POST'])

def usr():

    cid = current_user.get_id()

    uid = request.args.get('id')
    user = userTest.query.get_or_404(uid)  
    watchlist = db.session.query(userMovies, dtMovies).filter_by(uid=uid).outerjoin(dtMovies, userMovies.mid == dtMovies.id).order_by(userMovies.date_created.desc()).all()

    return render_template('usr.html', user=user, watchlist=watchlist, cid=cid)


@app.route('/user/<int:uid>', methods=['GET', 'POST'])
def user(uid):

    cid = current_user.get_id()

    user = userTest.query.get_or_404(uid)  
    watchlist = db.session.query(userMovies, dtMovies).filter_by(uid=uid).outerjoin(dtMovies, userMovies.mid == dtMovies.id).order_by(userMovies.date_created.desc()).all()

    return render_template('user.html', user=user, watchlist=watchlist, cid=cid)    

@app.route('/delete/<int:mid>')
@login_required
def delete(mid):

    uid = current_user.get_id()

    review_to_delete = userMovies.query.filter_by(uid=uid, mid=mid).first()

    print(uid)
    print(mid)
    print(review_to_delete)
    try:
        db.session.delete(review_to_delete)
        db.session.commit()
        return redirect('/dashboard')
    except:
        return 'There was a problem deleting that item'



@app.route('/update/<int:id>', methods=['GET', 'POST'])
@login_required
def update(id):
    movie = dtMovies.query.get_or_404(id)

    if request.method == 'POST':
        movie.movie_title = request.form['movie_title']
        movie.title_year = request.form['title_year']
        movie.country = request.form['country']
        movie.duration = request.form['duration']
        movie.director_name = request.form['director_name']
        movie.actor_1_name = request.form['actor_1_name']
        movie.actor_2_name = request.form['actor_2_name']
        movie.actor_3_name = request.form['actor_3_name']
        movie.genres = request.form['genres']
        movie.language = request.form['language']
        movie.content_rating = request.form['content_rating']
        movie.movie_imdb_link = request.form['movie_imdb_link']
        movie.imdb_score = request.form['imdb_score']

        try:
            db.session.commit()
            return redirect('/datatable')
        except:
            return 'There was an issue updating your movie'
    else:
        return render_template('update.html', movie=movie)


@app.route('/datatable/', methods=['GET', 'POST'])
def dt():
    movie_list = dtMovies.query.all()
    return render_template('datatable.html', movie_list=movie_list)



@app.errorhandler(404)
def page_not_found(e):
    return 'four oh four!'


if __name__ == "__main__":
    app.secret_key = 'super secret key'
    app.config['SESSION_TYPE'] = 'filesystem'

    app.run(debug=True)

