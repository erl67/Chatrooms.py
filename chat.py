#erl67
REBUILD_DB = False
FDEBUG = True

import os, re, json
from sys import stderr
from flask import Flask, g, send_from_directory, flash, render_template, abort, request, redirect, url_for, session, Response
from flask_debugtoolbar import DebugToolbarExtension
from sqlalchemy import or_
from datetime import datetime, date, timedelta
from dateutil import parser
from random import getrandbits
from models import db, populateDB, User, Room, Chat

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
    g.jchats = None
    g.j = None
    if 'uid' in session:
        g.user = User.query.filter_by(id=session['uid']).first()
        if g.user != None:
            g.rooms = Room.query.order_by(Room.lastmessage.asc()).all()
            if g.user.currentroom > 0:
                g.chats = Chat.query.filter(Chat.room == g.user.currentroom).order_by(Chat.created.asc()).all()
            else:
                g.chats = Chat.query.limit(10).all()
        g.jchats = Chat.as_json()
#         g.jchats = Chat.as_json().query.filter(Chat.room == g.user.currentroom)
    eprint("g.user: " + str(g.user))
    eprint("g.rooms: " + str(g.rooms))
    eprint("g.chats: " + str(g.chats))
    eprint("g.jchats: " + str(g.jchats))
#     g.j = json.dumps(str(g.jchats))
#     eprint("JSON.loads: " + str(g.j))
#     for c in Chat.query.all():
#         eprint (c.__dict__)
    
        
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
    if "uid" in session:
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
    msg += "\n\n"
    msg += Chat.Everything()
    return Response(render_template('test.html', testMessage=msg), status=203, mimetype='text/html')

@app.route('/')
def index():
    return Response(render_template('index.html'), status=203, mimetype='text/html')

@app.route('/rooms/')
def rooms():
    if g.user.currentroom == 0:
        return redirect(url_for("index"))
    else: 
        return redirect(url_for("joinroom", rid=g.user.currentroom))
    abort(404)

@app.route('/room/<int:rid>')
def joinroom(rid=None):
    if (not g.user or not rid):
        abort(404)
    elif (g.user.currentroom == rid):
        eprint(g.user.currentroom)
        room = Room.query.filter(Room.id == rid).first()
        chats = Chat.query.filter(Chat.room == room.id).order_by(Chat.created.asc()).all()
        return Response(render_template('/rooms/room.html', room=room, chats=chats), status=203, mimetype='text/html')
    else:
        room = Room.query.filter(Room.id == rid).first()
        if room == None:
            abort(404)
        else:
            chats = Chat.query.filter(Chat.room == room.id).order_by(Chat.created.asc()).all()
            user = User.query.filter(User.id == g.user.id).first()
            user.currentroom = room.id
            db.session.commit()
            return Response(render_template('/rooms/room.html', room=room, chats=chats), status=203, mimetype='text/html')
    return redirect(url_for("index"))

@app.route('/leaveroom/')
def exitroom():
    if not g.user:
        abort(404)
    else:
        user = User.query.filter(User.id == g.user.id).first()
        user.currentroom = 0
        try:
            db.session.commit()
            flash("Left room")
        except Exception as e:
            db.session.rollback()
            eprint (str(e))
            flash("Error leaving room")
    return redirect(url_for("index"))

@app.route('/newroom/', methods=["GET", "POST"])
def newroom():
    if not g.user:
        abort(404)
    elif request.method == "POST":
        POST_ROOM = remove_tags(str(request.form['room']))
        POST_CHAT = remove_tags(str(request.form['msg']))
        if POST_CHAT != None:
            newRoom = Room(POST_ROOM, g.user.id, None, None)
            eprint("newRoom: " + str(newRoom))
            db.session.add(newRoom)
            try:
                db.session.commit()
                newChat = Chat(newRoom.id, g.user.id, None, POST_CHAT)
                eprint("newChat: " + str(newChat))
                db.session.add(newChat)
                try:
                    db.session.commit()
                    flash ("Created room: " + str(newRoom.roomname))
                    return redirect(url_for("index"))
                except Exception as e:
                    db.session.rollback()
                    eprint(str(e))
                    flash("Error adding message to new room")
                    return redirect(url_for("newroom"))
            except Exception as e:
                flash("Room creation failed")
        else:
            flash("Must enter initial message")
    return Response(render_template('/rooms/newRoom.html'), status=203, mimetype='text/html')

@app.route('/chat')
def get_chat():
    return json.dumps(g.jchats, default=json_serial)

@app.route("/new_msg", methods=["POST"])
def add():
    chat.append([request.json["message"]])
    return "OK!"

@app.route("/chats")
def get_items():
    return str(len(g.jchats))
#     return json.dumps(g.rooms)

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

def json_serial(obj):
    """JSON serializer for objects not serializable by default json code stackoverflow.com/a/22238613/7491839 """
    if isinstance(obj, (datetime, date)):
        return obj.isoformat()
    raise TypeError ("Type %s not serializable" % type(obj))
    
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