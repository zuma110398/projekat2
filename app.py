
from flask import Flask, render_template, request, redirect, url_for, session, flash
from flask_mysqldb import MySQL
import flask_bootstrap
import yaml
from passlib.hash import sha256_crypt

app = Flask(__name__)
app.secret_key = 'tajni_kljuc'
flask_bootstrap.Bootstrap(app)

db = yaml.safe_load(open('db.yaml'))
app.config['MYSQL_HOST'] = 'localhost'
app.config['MYSQL_USER'] = 'root'
app.config['MYSQL_PASSWORD'] = 'root'
app.config['MYSQL_DB'] = 'bolnica2'

mysql = MySQL(app)


@app.route('/')
def home():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        ime = request.form['ime']
        prezime = request.form['prezime']
        email = request.form['email']
        broj_telefona = request.form['broj_telefona']
        raw_password = request.form['password']
        hashed_password = sha256_crypt.hash(raw_password)

        cur = mysql.connection.cursor()

        # Provjera postoji li korisnik s danim emailom
        cur.execute("SELECT * FROM pacijenti WHERE email = %s", (email,))
        existing_user = cur.fetchone()

        if existing_user:
            flash('Korisnik sa ovim emailom već postoji.', 'error')
            return redirect(url_for('register'))

        # Unos novog korisnika
        cur.execute("INSERT INTO pacijenti (ime, prezime, email, broj_telefona, password) VALUES (%s, %s, %s, %s, %s)",
                    (ime, prezime, email, broj_telefona, hashed_password))
        mysql.connection.commit()
        cur.close()

        flash('Registracija uspjesna! Mozete se prijaviti.', 'success')
        return redirect(url_for('login'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        try:
            cur = mysql.connection.cursor(dictionary=True)
            cur.execute("SELECT * FROM pacijenti WHERE email = %s", (email,))
            user = cur.fetchone()
            cur.close()

            if user:
                if sha256_crypt.verify(password, user['password']):
                    print("Login successful!")  # Add this line for debugging
                    session['login'] = True
                    session['ime'] = user['ime']
                    session['prezime'] = user['prezime']
                    session['email'] = user['email']
                    session['user_id'] = user['id']
                    mysql.connection.commit()

                    cur = mysql.connection.cursor()
                    cur.execute("UPDATE pacijenti SET active = 1 WHERE email = %s", [email])
                    mysql.connection.commit()
                    cur.close()

                    return redirect(url_for('dashboard'))
                else:
                    flash('Pogrešna lozinka. Pokušajte ponovo.', 'error')
            else:
                flash('Korisnik s ovim emailom nije pronađen.', 'error')

        except Exception as e:
            print("Error:", e)

    return render_template('login.html')


@app.route('/dashboard')
def dashboard():
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM pacijenti WHERE id = %s", (session['user_id'],))
        user = cur.fetchone()
        cur.close()

        if user:
            return render_template('dashboard.html', user=user)
        else:
            flash('Niste logovani', 'error')
            return redirect(url_for('login'))
    else:
        flash('Trebate se logovati', 'error')
        return redirect(url_for('login'))


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('user_email', None)
    return redirect(url_for('login'))


@app.route('/termin/<int:id>')
def termin(id):
    if 'user_id' in session:
        cur = mysql.connection.cursor()
        result_value = cur.execute("SELECT * FROM termini WHERE id = %s", [id])
        if result_value > 0:
            termin_info = cur.fetchone()
            return render_template('termin.html', termin=termin_info)
        flash('Termin nije pronađen', 'error')
        return redirect(url_for('dashboard'))
    else:
        flash('Trebate se logovati', 'error')
        return redirect(url_for('login'))


@app.route('/termini', methods=['GET'])
def pregledtermina():
    if 'user_id' in session:
        user_id = session['user_id']
        cur = mysql.connection.cursor()
        cur.execute("SELECT * FROM termini WHERE pacijent_id = %s", [user_id])
        termini = cur.fetchall()
        cur.close()
        return render_template('termini.html', termini=termini)
    else:
        flash('Trebate se logovati', 'error')
        return redirect(url_for('login'))


@app.route('/dodajtermin', methods=['GET', 'POST'])
def dodajtermin():
    if 'user_id' in session:
        if request.method == 'POST':
            cur = mysql.connection.cursor()
            doctor_id = request.form.get('doctor_id')
            termin_date = request.form.get('termin_date')
            pacijent_id = session['user_id']

            cur.execute("INSERT INTO termini(doktor_id, pacijent_id, termin_date) VALUES (%s, %s, %s)",
                        [doctor_id, pacijent_id, termin_date])
            mysql.connection.commit()
            cur.close()
            flash('Termin kreiran!', 'success')
            return redirect(url_for('dashboard'))
        else:
            cur = mysql.connection.cursor()
            cur.execute("SELECT * FROM doktori")
            doctors = cur.fetchall()
            cur.close()
            return render_template("dodajtermin.html", doctors=doctors)
    else:
        flash('Trebate se logovati', 'error')
        return redirect(url_for('login'))


if __name__ == '__main__':
    app.run(debug=True)
