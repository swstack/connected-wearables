from flask import Flask, render_template, session, request, redirect
from cwear.db.model import User, DatabaseManager
import os

HAPI_CLIENT_ID = os.environ.get('HAPI_CLIENT_ID')

db_manager = DatabaseManager()

app = Flask(__name__, static_url_path="")
app.debug = True
app.secret_key = "1234"


def requires_admin(fn):
    """Decorator to be applied to routes that require administrator login"""

    def ensure_admin(*args, **kwargs):
        if session.get('user') is None:
            return redirect('/login')
        else:
            return fn(*args, **kwargs)

    return ensure_admin


@app.route('/')
def index():
    return render_template('index.html', hapi_client_id=HAPI_CLIENT_ID)


@app.route('/login', methods=["GET", "POST"])
def login():
    db = db_manager.get_db_session()

    if request.method == "GET":
        return render_template('login.html')
    else:
        username = request.form.get("user")
        password = request.form.get("passwd")
        create_admin_user = (request.form.get("admin") == "on")
        if username:
            user = db.query(User).filter_by(name=username).first()
            if user is None:
                if create_admin_user:
                    db.add(User(name=username, password=password,
                                admin=create_admin_user))
                    db.commit()
                    session["user"] = username
                    return redirect("/dashboard")
            else:
                if password == user.password:
                    session["user"] = username
                    return redirect("/dashboard")

        return redirect(('/login'))


@app.route('/logout')
def logout():
    session['user'] = None
    return redirect('/')


@app.route('/dashboard')
@requires_admin
def dashboard():
    return render_template('dashboard.html')


if __name__ == "__main__":
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)