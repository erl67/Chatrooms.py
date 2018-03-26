#erl67
REBUILD_DB = True
FDEBUG = True

import os, re, json
from sys import stderr
from flask import Flask, g, send_from_directory, flash, render_template, abort, request, redirect, url_for, session, Response
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import or_
from datetime import datetime, timedelta
from dateutil import parser
from random import getrandbits
from models import db, User, Room, populateDB

chat = []

def create_app():
    app = Flask(__name__)
    DB_NAME = os.path.join(app.root_path, 'chat.db')
    
    app.config.update(dict(
        SQLALCHEMY_TRACK_MODIFICATIONS=False,
        SECRET_KEY='erl67_',
        TEMPLATES_AUTO_RELOAD=True,
        SQLALCHEMY_DATABASE_URI='sqlite:///' + DB_NAME
    ))
    
    db.init_app(app)
    
    if REBUILD_DB == True and os.access(DB_NAME, os.W_OK):
        os.remove(DB_NAME)
        print('DB Dropped')
        
    if os.access(DB_NAME, os.W_OK):
        print('DB Exists')
    else:
        app.app_context().push()
        db.drop_all()
        db.create_all()
        print('DB Created')
        populateDB()
    print(app.__str__(), end="  ")
    return app

app = create_app()

@app.cli.command('initdb')
def initdb_command():
    db.drop_all()
    db.create_all()
    populateDB()
    print('Initialized the database.')
    
@app.before_request
def before_request():
    g.user = None
    g.rooms = None
    g.chats = None
    if 'uid' in session:
        g.user = User.query.filter_by(id=session['uid']).first()
        if g.user != None:
            g.rooms = Room.query.order_by(Room.lastmessage.asc()).all()
    eprint("g.user: " + str(g.user))
    eprint("g.rooms: " + str(g.rooms))
    
        
@app.before_first_request
def before_first_request():
    eprint("    🥇")
    
@app.context_processor
def utility_processor():
    def getName(id):
        user = User.query.filter(User.id==id).first()
        if user != None:
            return user.username
        else:
            return ""
    return dict(getName=getName)


@app.route("/register/", methods=["GET", "POST"])
def signer():
    if g.user:
        flash("Already logged in!")
        return redirect(url_for("index"))
    #elif request.method == "GET":
        #flash("Complete form to register")
    elif request.method == "POST":
        POST_USER = remove_tags(str(request.form['user']))
        POST_PASS = remove_tags(str(request.form['pass']))
        POST_EMAIL = remove_tags(str(request.form['mail']))
        if POST_USER != None and POST_PASS != None:
            newUser = User(POST_USER, POST_PASS, POST_EMAIL)
            db.session.add(newUser)
            try:
                db.session.commit()
                if User.query.filter(User.username == POST_USER, User.password == POST_PASS):
                    flash("Successfully registered! " + POST_USER + ":" + POST_PASS)
                    session["uid"] = User.query.filter(User.username == POST_USER).first().id
                    return redirect(url_for("index"))
            except Exception as e:
                db.session.rollback()
                eprint(str(e))
                flash("Error adding to database")
        else:
            flash("Error registering new account")
    return Response(render_template("accounts/newAccount.html"), status=200, mimetype='text/html')

@app.route("/login/", methods=["GET", "POST"])
def logger():
    if "username" in session:
        flash("Already logged in!")
        return redirect(url_for("index"))
    elif request.method == "POST":
        POST_USER = str(request.form['user'])
        POST_PASS = str(request.form['pass'])
        valid = User.query.filter(User.username == POST_USER, User.password == POST_PASS).first()
        eprint(str(valid))
        if (POST_USER == "owner") and (POST_PASS == "pass"):
            session["uid"] = 1
            flash("Successfully logged in as Mr. Manager")
            return redirect(url_for("rooms"))
        elif valid is not None:
            session["uid"] = valid.id
            flash("Successfully logged in!  " + valid.username)
            return redirect(url_for("rooms", uid=valid.id))
        else:
            flash("Error logging you in!")
    return Response(render_template("accounts/loginPage.html"), status=200, mimetype='text/html')

@app.route("/logout/")
def unlogger():
    if "uid" in session:
        session.clear()
        flash("Successfully logged out!")
        return redirect(url_for("index"))
    else:
        session.clear()
        flash("Not currently logged in!")
        return redirect(url_for("logger"))
    
@app.route("/db/")
def rawstats():
    msg = ""
    msg += User.Everything()
    msg += "\n\n"
    msg += Room.Everything()
    return Response(render_template('test.html', testMessage=msg), status=203, mimetype='text/html')

@app.route('/')
def index():
    return Response(render_template('base.html'), status=203, mimetype='text/html')

@app.route('/rooms/')
def rooms():
    return Response(render_template('/rooms/rooms.html', rooms=g.rooms), status=203, mimetype='text/html')

@app.route('/join/<int:rid>')
def joinroom():
    return Response(render_template('/rooms/rooms.html', rooms=g.rooms), status=203, mimetype='text/html')

@app.route('/chat')
def get_chat():
    return json.dumps(text)

@app.route("/new_msg", methods=["POST"])
def add():
    chat.append([request.json["message"]])
    return "OK!"

@app.route("/chatter")
def get_items():
    return json.dumps(chat)

@app.errorhandler(403)
@app.errorhandler(404)
def page_not_found(error):
    return Response(render_template('404.html', errno=error), status=404, mimetype='text/html')

@app.errorhandler(405)
def wrong_method(error):
    return Response("You shouldn't have done that", status=405, mimetype='text/html')

@app.route('/418/')
def err418(error=None):
    return Response(render_template('404.html', errno=error), status=418, mimetype='text/html')

@app.route('/favicon.ico') 
def favicon():
    if bool(getrandbits(1))==True:
        return send_from_directory(os.path.join(app.root_path, 'static'), 'favicon.ico', mimetype='image/vnd.microsoft.icon')
    else:
        return send_from_directory(os.path.join(app.root_path, 'static'), 'faviconF.ico', mimetype='image/vnd.microsoft.icon')

def eprint(*args, **kwargs):
    print(*args, file=stderr, **kwargs)
    
TAG_RE = re.compile(r'<[^>]+>')
def remove_tags(text):
    return TAG_RE.sub('', text)
    
if __name__ == "__main__":
    print('Starting......')
    if FDEBUG==True:
        app.config.update(dict(
            DEBUG=True,
            DEBUG_TB_INTERCEPT_REDIRECTS=False,
            SQLALCHEMY_TRACK_MODIFICATIONS=True,
            TEMPLATES_AUTO_RELOAD=True,
        ))
        app.jinja_env.auto_reload = True
        toolbar = DebugToolbarExtension(app) 
        app.run(use_reloader=True, host='0.0.0.0')
    else:
        app.run()