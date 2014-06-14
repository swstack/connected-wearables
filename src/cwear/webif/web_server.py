import os
from flask import Flask, render_template, session, request, redirect
from flask.ext.sqlalchemy import SQLAlchemy

HAPI_CLIENT_ID = os.environ.get('HAPI_CLIENT_ID')

app = Flask(__name__, static_url_path="")
app.secret_key = "1234"
db = SQLAlchemy(app)


class User(db.Model):
    __tablename__ = "user"

    id = db.Column(db.INTEGER, primary_key=True, autoincrement=True)
    name = db.Column(db.TEXT, unique=True)
    password = db.Column(db.TEXT)
    admin = db.Column(db.BOOLEAN, default=False)


def requires_admin(fn):
    """Decorator to be applied to routes that require administrator login

    """
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
    if request.method == "GET":
        return render_template('login.html')
    else:
        username = request.form.get("user")
        password = request.form.get("passwd")
        create_admin_user = (request.form.get("admin") == "on")
        if username:
            user = User.query.filter_by(name=username).first()
            if user is None:
                if create_admin_user:
                    db.session.add(User(name=username, password=password, admin=create_admin_user))
                    db.session.commit()
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