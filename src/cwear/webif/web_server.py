import sys
import os

THIS_DIR = os.path.dirname(__file__)

sys.path.append(os.path.join(THIS_DIR, "..", ".."))

import functools
from flask import Flask, render_template, session, request, redirect, url_for, \
    flash
from cwear.db.model import User, DatabaseManager, CwearApplication, \
    HumanApiAccount, DeviceCloudAccount


HAPI_CLIENT_ID = os.environ.get('HAPI_CLIENT_ID')

db_manager = DatabaseManager()

app = Flask(__name__, static_url_path="")
app.debug = True
app.secret_key = "1234"


def logged_in(fn):
    """Decorator to be applied to routes that require administrator login"""

    @functools.wraps(fn)
    def ensure_admin(*args, **kwargs):
        userid = session.get('user_id')
        if userid:
            db = db_manager.get_db_session()
            user = db.query(User).get(userid)
            if user:
                return fn(*args, **kwargs)

        session["user"] = None
        session["user_id"] = None
        return redirect('/login')

    return ensure_admin


def get_current_user():
    """Get information about the currently logged in user (or return None)"""
    db = db_manager.get_db_session()
    username = session.get("user")
    if username is not None:
        userdata = db.query(User).filter_by(name=username).first()
        return userdata
    return None


@app.route('/')
def index():
    return redirect('/dashboard')


@app.route('/login', methods=["GET", "POST"])
def login():
    db = db_manager.get_db_session()

    if request.method == "GET":
        return render_template('login.html')
    else:
        username = request.form.get("user")
        password = request.form.get("passwd")
        if username and password:
            user = db.query(User).filter_by(name=username).first()
            if user is None:
                user = User(name=username, password=password, admin=True)
                db.add(user)
                db.commit()
                session["user"] = user.name
                session["user_id"] = user.id
                flash("A new admin account created for %s" % user.name)
                return redirect("/dashboard")
            else:
                if password == user.password:
                    session["user"] = user.name
                    session["user_id"] = user.id
                    flash("Welcome.")
                    return redirect("/dashboard")
                else:
                    flash("Provided username or password was not correct")
        else:
            flash("You must specify a username and password!")

        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session['user'] = None
    return redirect('/')


@app.route('/dashboard')
@logged_in
def dashboard():
    db = db_manager.get_db_session()
    user = db.query(User).filter_by(name=session.get('user')).first()
    apps = db.query(CwearApplication).filter_by(owner=user.id)
    if apps is None:
        apps = []

    return render_template('dashboard.html', **{
        "apps": apps,
    })


@app.route('/app/<name>', methods=["GET", "POST"])
@logged_in
def appconfig(name):
    db = db_manager.get_db_session()

    if request.method == "GET":
        app = db.query(CwearApplication).filter_by(name=name).first()
        context = {
            "app": app
        }
        return render_template('appcfg.html', **context)
    else:
        dcuser = request.form.get('dcuser')
        dcpass = request.form.get('dcpass')
        hapiapp = request.form.get('hapiapp')
        hapiclient = request.form.get('hapiclient')
        syncfreq = request.form.get('syncfreq')

        if dcuser and dcpass and hapiapp and hapiclient and syncfreq:
            cwearapp = db.query(CwearApplication).filter_by(name=name).first()
            hapiaccount = HumanApiAccount(app_key=hapiapp, client_id=hapiclient)
            dcaccount = DeviceCloudAccount(username=dcuser, password=dcpass)
            db.add(hapiaccount)
            db.add(dcaccount)
            cwearapp.related_hapiaccount = hapiaccount
            cwearapp.related_dcaccount = dcaccount
            db.commit()
            flash('Updated Successfully.')
        else:
            flash('Incomplete data')

        return redirect("/app/%s" % name)


@app.route('/create_app', methods=["POST"])
@logged_in
def add_app():
    db = db_manager.get_db_session()
    appname = request.form.get("appname")
    if appname:
        newapp = CwearApplication(owner=session['user_id'], name=appname)
        db.add(newapp)
        db.commit()

    return redirect("/dashboard")


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
