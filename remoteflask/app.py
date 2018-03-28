from flask import Flask, render_template, redirect, url_for ,request
from flask_bootstrap import Bootstrap
from flask_wtf import FlaskForm 
from wtforms import StringField, PasswordField, BooleanField,SelectField
from wtforms.validators import InputRequired, Email, Length
from flask_sqlalchemy  import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
import datetime

app = Flask(__name__)
app.config['SECRET_KEY'] = 'Thisissupposedtobesecret!'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///database.sqlite'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
bootstrap = Bootstrap(app)
db = SQLAlchemy(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'


class report(db.Model):
    id = db.Column(db.Integer, primary_key=True)    
    divice = db.Column(db.String(15))
    starTime = db.Column(db.String(15))
    stopTime = db.Column(db.String(15))
    timeDeference =  db.Column(db.String(15))
    statMessage = db.Column(db.String(15))
    stopMessage = db.Column(db.String(15))
    active =  db.Column('is_active', db.Boolean(), nullable=False, server_default='0')


class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(15), unique=True)
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(80))
    mode = db.Column(db.String(10))
    topic = db.Column(db.String(10))


class UserLog(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    usename = db.Column(db.String(15))
    LoginTime = db.Column(db.String(15))
    LogoutTime = db.Column(db.String(15))


class Map(UserMixin,db.Model):
    id = db.Column(db.Integer, primary_key = True) 
    device = db.Column(db.String(15))
    bed = db.Column(db.String(15))
    dept = db.Column(db.String(15))

class NCS_Reading(db.Model):
    id = db.Column(db.Integer, primary_key = True) 
    message = db.Column(db.String(15))
    date = db.Column(db.String(15))
    time = db.Column(db.String(15))
    bed = db.Column(db.String(15))



@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

class LoginForm(FlaskForm):
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    remember = BooleanField('remember me')

class RegisterForm(FlaskForm):
    email = StringField('email', validators=[InputRequired(), Email(message='Invalid email'), Length(max=50)])
    username = StringField('username', validators=[InputRequired(), Length(min=4, max=15)])
    password = PasswordField('password', validators=[InputRequired(), Length(min=8, max=80)])
    mode = SelectField(u'Mode', choices=[('ADMIN', 'ADMIN'), ('NORMAL', 'NORMAL')])
    topic = SelectField(u'Topic', choices = [('crv','CRV'),('clz','CLZ'),('fwd','FWD'),('mwd','MWD'),('cab','CAB'),('dng','DNG'),('dps','DPS'),('dcu','DCU'),('ccu','CCU')])

class MapInsertfrom(FlaskForm):
    device = StringField('device', validators=[InputRequired()] )
    dept = SelectField(u'Topic', choices = [('crv','CRV'),('clz','CLZ'),('fwd','FWD'),('mwd','MWD'),('cab','CAB'),('dng','DNG'),('dps','DPS'),('dcu','DCU'),('ccu','CCU')])
    bed = StringField('bed', validators=[InputRequired()])


@app.route('/test')
def test():
    return '<h1>test1</h1>'


@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user:
            if check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                userLog = UserLog(usename=form.username.data , LoginTime = datetime.datetime.now() )
                db.session.add(userLog)
                db.session.commit()
                return redirect(url_for('dashboard'))

        return '<h1>Invalid username or password</h1>'
        #return '<h1>' + form.username.data + ' ' + form.password.data + '</h1>'

    return render_template('login.html', form=form)


@app.route('/maplist')
def maplist():
    data = Map.query.all()
    return render_template('maplist.html',datas = data)

@app.route('/mapinsert', methods =['GET','POST'])
def mapinsert():
    form = MapInsertfrom()
    if form.validate_on_submit():
        maptem = Map(device = 'CO'+form.device.data , dept = form.dept.data , bed = form.bed.data)
        db.session.add(maptem)
        db.session.commit()

    return render_template('insertmap.html',form=form)


@app.route('/mapupdate/<id>', methods = ['GET','POST'])
def mapupdate(id):
    temmap = Map.query.filter_by(id =id).first()
    form = MapInsertfrom()
    if form.validate():
      # temmap.device = 'hello'
       # temmap.bed = '123'
        form.populate_obj(temmap)
    return render_template('mapupdate.html',form=form)


@app.route('/signup', methods=['GET', 'POST'])
def signup():
    form = RegisterForm()

    if form.validate_on_submit():
        hashed_password = generate_password_hash(form.password.data, method='sha256')
        new_user = User(username=form.username.data, email=form.email.data, password=hashed_password,mode = form.mode.data, topic= form.topic.data )
        print(type(new_user))
        db.session.add(new_user)
        db.session.commit()

        return '<h1>New user has been created!</h1>'
        #return '<h1>' + form.username.data + ' ' + form.email.data + ' ' + form.password.data + '</h1>'

    return render_template('signup.html', form=form)

@app.route('/dashboard')
@login_required
def dashboard():
    return render_template('dashboard.html', name=current_user.username)

@app.route('/logout')
@login_required
def logout():
    userLog = UserLog.query.filter_by(usename=current_user.username).order_by('-id').first()
    userLog.LogoutTime = datetime.datetime.now() 
    db.session.add(userLog)
    db.session.commit()
    logout_user()
    return redirect(url_for('index'))

if __name__ == '__main__':
   # db.drop_all()
    db.create_all()
    db.session.commit()
    app.run(host= '0.0.0.0',debug=True)
