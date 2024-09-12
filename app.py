from flask import Flask, render_template, request, redirect, url_for, session, json
from flask_mail import Mail, Message
from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime, timedelta
import os
import secrets
import mysql.connector
import pytz
from werkzeug.utils import secure_filename
import pymysql

pymysql.install_as_MySQLdb()
SQLALCHEMY_DATABASE_URI = 'mysql+pymysql://root@localhost/salon'

local_tz = pytz.timezone('Asia/Jerusalem')

app = Flask(__name__)
secret_key = secrets.token_hex(32)
app.secret_key = os.getenv('SECRET_KEY', secret_key)

# Mail configuration
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = os.environ.get('MAIL_USERNAME')
app.config['MAIL_PASSWORD'] = os.environ.get('MAIL_PASSWORD')
app.config['MAIL_DEFAULT_SENDER'] = ('Salon App', os.environ.get('MAIL_USERNAME'))

mail = Mail(app)

# Scheduler configuration
scheduler = BackgroundScheduler()

print(datetime.now(local_tz))


# Function to connect to the database
def connect_db():
    return pymysql.connect(host="localhost", user="root", password="", db="salon")


# Define the path to the translations directory
TRANSLATIONS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'translations')


def load_translation(language):
    with open(os.path.join(TRANSLATIONS_DIR, f"{language}.json"), "r", encoding="utf-8") as file:
        return json.load(file)


@app.route('/')
def home():
    # Get language from query params or session
    language = request.args.get('lang', session.get('lang', 'en'))
    session['lang'] = language  # Save language in session

    translations = load_translation(language)

    return render_template('index.html', translations=translations, lang=language)


@app.route('/change_language/<lang_code>')
def change_language(lang_code):
    session['lang'] = lang_code  # Set language in session
    return redirect(url_for('home'))  # Redirect back to homepage


@app.route('/appointments')
def show_appointments():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    language = session.get('lang', 'en')
    translations = load_translation(language)

    selected_date = request.args.get('date')

    # Convert the selected_date to a datetime object for querying the database
    selected_date_start = datetime.strptime(selected_date, '%Y-%m-%d')
    selected_date_end = selected_date_start + timedelta(days=1)

    # Connect to the database
    db = connect_db()
    cursor = db.cursor()

    # Check if the logged-in user is a customer or shop owner
    if session['role'] == 'customer':
        # Query appointments for the logged-in customer on the selected date, sorted by the soonest appointment first
        cursor.execute("""
            SELECT users.username, services.service_name, appointments.appointment_date 
            FROM appointments 
            JOIN users ON appointments.customer_id = users.id
            JOIN services ON appointments.service_id = services.id
            WHERE appointments.customer_id = %s
            AND appointments.appointment_date >= %s 
            AND appointments.appointment_date < %s
            ORDER BY appointments.appointment_date ASC  -- Sort by the soonest appointment first
        """, (session['user_id'], selected_date_start, selected_date_end))

    elif session['role'] == 'shop_owner':
        # Query appointments for the shop(s) owned by the logged-in shop owner on the selected date, sorted by the
        # soonest appointment first
        cursor.execute("""
            SELECT users.username, services.service_name, appointments.appointment_date 
            FROM appointments 
            JOIN users ON appointments.customer_id = users.id
            JOIN services ON appointments.service_id = services.id
            JOIN shops ON appointments.shop_id = shops.id
            WHERE shops.owner_id = %s
            AND appointments.appointment_date >= %s 
            AND appointments.appointment_date < %s
            ORDER BY appointments.appointment_date ASC  -- Sort by the soonest appointment first
        """, (session['user_id'], selected_date_start, selected_date_end))

    appointments = cursor.fetchall()
    db.close()

    # Format the appointments for display
    appointment_list = [
        {"customer_name": appointment[0], "service_name": appointment[1],
         "appointment_time": appointment[2].strftime("%H:%M %p")}
        for appointment in appointments
    ]

    return render_template('appointments.html', translations=translations, lang=language,
                           appointments=appointment_list, selected_date=selected_date)


# Mock function for querying appointments (replace this with actual database logic)
def query_appointments_by_date(date):
    # For demonstration, return a list of example appointments for a specific date
    return [
        {"customer_name": "John Doe", "service_name": "Haircut", "appointment_time": "10:00 AM"},
        {"customer_name": "Jane Smith", "service_name": "Nail Polish", "appointment_time": "2:00 PM"}
    ]


@app.route('/send_test_email')
def send_test_email():
    msg = Message('Test Email', recipients=[os.environ.get('MAIL_USERNAME')])
    msg.body = 'This is a test email from the Salon App.'

    try:
        mail.send(msg)
        return 'Test email sent successfully!'
    except Exception as e:
        return f'Failed to send email: {str(e)}'


# Function to send email reminders
def send_email_reminder(recipient, appointment_time, shop_name):
    subject = "Appointment Reminder"
    body = f"Dear customer, this is a reminder of your appointment at {shop_name} scheduled for {appointment_time}."

    msg = Message(subject, recipients=[recipient])
    msg.body = body

    try:
        mail.send(msg)
        print(f"Reminder sent to {recipient} for appointment on {appointment_time}")
    except Exception as e:
        print(f"Failed to send email: {e}")


# Function to schedule email reminders
# Function to schedule email reminders
def schedule_email_reminders():
    print("Scheduler is running...")

    with app.app_context():  # Ensure Flask application context is available
        db = connect_db()
        cursor = db.cursor()

        # Get the current UTC time
        now_utc = datetime.now(pytz.utc)

        # Convert UTC to your local time zone
        local_tz = pytz.timezone('Asia/Jerusalem')
        now_local = now_utc.astimezone(local_tz)

        # Get future time (next 24 hours) in local time zone
        future_time_local = now_local + timedelta(hours=24)

        print(f"Checking appointments between {now_local} and {future_time_local}")  # Debugging

        # Convert times back to UTC for the database query
        now_utc_for_db = now_local.astimezone(pytz.utc)
        future_time_utc_for_db = future_time_local.astimezone(pytz.utc)

        cursor.execute("""
            SELECT appointments.id, appointments.appointment_date, users.email, shops.name
            FROM appointments
            JOIN users ON appointments.customer_id = users.id
            JOIN shops ON appointments.shop_id = shops.id
            WHERE appointments.appointment_date BETWEEN %s AND %s
            AND appointments.status = 'confirmed'
        """, (now_utc_for_db, future_time_utc_for_db))

        upcoming_appointments = cursor.fetchall()

        if not upcoming_appointments:
            print("No upcoming appointments.")
        else:
            for appointment in upcoming_appointments:
                appointment_time = appointment[1]
                customer_email = appointment[2]
                shop_name = appointment[3]

                # Convert appointment time to local time for email display
                appointment_time_local = appointment_time.astimezone(local_tz)

                send_email_reminder(customer_email, appointment_time_local.isoformat(), shop_name)
                print(f"Reminder sent to {customer_email} for appointment on {appointment_time_local}")

        db.close()


# Schedule the task to run every minute
scheduler.add_job(schedule_email_reminders, 'interval', hours=24)
scheduler.start()


# Homepage route
@app.route('/')
def index():
    return render_template('index.html')


@app.route('/register', methods=['GET', 'POST'])
def register():
    language = session.get('lang', 'en')  # Default to English
    translations = load_translation(language)

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        email = request.form['email']
        role = request.form['role']

        # Handle file upload
        profile_picture = request.files.get('profile_picture')
        profile_picture_filename = None

        # If no profile picture is uploaded, assign a default one
        if profile_picture and profile_picture.filename != '':
            if allowed_file(profile_picture.filename):
                # Save the uploaded file
                filename = secure_filename(profile_picture.filename)
                profile_picture.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                profile_picture_filename = filename
        else:
            # Assign default image if none uploaded
            profile_picture_filename = 'default_profile.jpg'  # Assuming this is the default image in 'static/uploads/'

        # Connect to the database
        db = connect_db()
        cursor = db.cursor()

        # Insert the new user into the database
        cursor.execute("""
            INSERT INTO users (username, password, email, role, profile_picture)
            VALUES (%s, %s, %s, %s, %s)
        """, (username, password, email, role, profile_picture_filename))

        db.commit()
        db.close()

        return redirect(url_for('login'))

    return render_template('register.html', translations=translations, lang=language)


@app.route('/logout')
def logout():
    # Clear the session
    session.clear()
    # Redirect to the index page
    return redirect(url_for('index'))


# Login route
@app.route('/login', methods=['GET', 'POST'])
def login():
    # Get language from query params or session
    language = request.args.get('lang', session.get('lang', 'en'))
    session['lang'] = language  # Save language in session

    translations = load_translation(language)

    if request.method == 'POST':
        # Login logic
        username = request.form['username']
        password = request.form['password']

        db = connect_db()
        cursor = db.cursor()
        cursor.execute("SELECT * FROM users WHERE username=%s AND password=%s", (username, password))
        user = cursor.fetchone()
        db.close()

        if user:
            session['user_id'] = user[0]
            session['role'] = user[4]  # role from db (customer or shop_owner)
            return redirect(url_for('dashboard'))
        else:
            return 'Invalid login'
    return render_template('login.html', translations=translations, lang=language)


@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    # Load translation based on session language
    language = session.get('lang', 'en')  # default to English if not set
    translations = load_translation(language)

    db = connect_db()
    cursor = db.cursor()

    # Fetch the user information including profile_picture
    cursor.execute("SELECT username, profile_picture FROM users WHERE id = %s", (session['user_id'],))
    user_data = cursor.fetchone()

    # Extract username and profile picture from the query result
    username = user_data[0]
    profile_picture = user_data[1]  # Fetch profile_picture

    # Admin Dashboard
    if session['role'] == 'admin':
        db.close()
        return redirect(url_for('admin'))

    # Shop Owner Dashboard
    elif session['role'] == 'shop_owner':
        # Fetch shops owned by the shop owner
        cursor.execute("SELECT id, name, address, phone FROM shops WHERE owner_id = %s", (session['user_id'],))
        shops = cursor.fetchall()

        # Get current date in YYYY-MM-DD format
        current_date = datetime.now().date()

        # Fetch appointments for today for each shop owned by the shop owner
        cursor.execute("""
            SELECT appointments.appointment_date, users.username, services.service_name, appointments.status 
            FROM appointments 
            JOIN users ON appointments.customer_id = users.id 
            JOIN services ON appointments.service_id = services.id 
            WHERE appointments.shop_id IN (SELECT id FROM shops WHERE owner_id = %s)
            AND DATE(appointments.appointment_date) = %s
            """, (session['user_id'], current_date))

        today_appointments = cursor.fetchall()

        shop_data = []
        for shop in shops:
            shop_dict = {
                'id': shop[0],
                'name': shop[1],
                'address': shop[2],
                'phone': shop[3],
                'services': [],
                'appointments': []
            }

            # Fetch services for each shop
            cursor.execute("SELECT service_name, price, duration FROM services WHERE shop_id = %s", (shop[0],))
            services = cursor.fetchall()
            for service in services:
                shop_dict['services'].append({
                    'service_name': service[0],
                    'price': service[1],
                    'duration': service[2]
                })

            # Fetch appointments for each shop, including service details
            cursor.execute("""
                SELECT appointments.id, appointments.appointment_date, appointments.status, users.username, services.service_name
                FROM appointments
                JOIN users ON appointments.customer_id = users.id
                JOIN services ON appointments.service_id = services.id
                WHERE appointments.shop_id = %s
            """, (shop[0],))
            appointments = cursor.fetchall()

            for appointment in appointments:
                shop_dict['appointments'].append({
                    'id': appointment[0],
                    'appointment_date': appointment[1].isoformat(),
                    'status': appointment[2],
                    'customer_name': appointment[3],
                    'service_name': appointment[4]
                })

            shop_data.append(shop_dict)

        db.close()

        # Rendering the updated dashboard with today's appointments
        return render_template('dashboard.html', shops=shop_data, username=username, profile_picture=profile_picture,
                               today_appointments=today_appointments, translations=translations, lang=language)

    # Customer Dashboard
    else:
        # Fetch the list of approved shops (only show shops where is_approved = TRUE)
        cursor.execute("SELECT id, name, address, phone, image FROM shops WHERE is_approved = TRUE")
        shops = cursor.fetchall()

        # Fetch appointments for the customer
        cursor.execute("""
            SELECT appointments.appointment_date, appointments.status, shops.name
            FROM appointments
            JOIN shops ON appointments.shop_id = shops.id
            WHERE customer_id = %s
        """, (session['user_id'],))
        appointments = cursor.fetchall()

        customer_appointments = []
        for appointment in appointments:
            customer_appointments.append({
                'shop_name': appointment[2],  # Shop name
                'appointment_date': appointment[0].isoformat(),  # ISO format for FullCalendar
                'status': appointment[1]  # Appointment status
            })

        db.close()
        return render_template('dashboard.html', shops=shops, appointments=customer_appointments,
                               username=username, profile_picture=profile_picture, translations=translations,
                               lang=language)


@app.route('/add_shop', methods=['GET', 'POST'])
def add_shop():
    if 'user_id' not in session or session['role'] != 'shop_owner':
        return redirect(url_for('login'))

    # Get the language from the session or default to 'en'
    language = session.get('lang', 'en')

    # Load the translations
    translations = load_translation(language)

    if request.method == 'POST':
        shop_name = request.form['shop_name']
        address = request.form['address']
        phone = request.form['phone']

        # Check if an image file was uploaded
        if 'image' not in request.files:
            flash('No file part')
            return redirect(request.url)
        image_file = request.files['image']

        if image_file and allowed_file(image_file.filename):
            # Secure the filename and save it to the uploads folder
            filename = secure_filename(image_file.filename)
            image_file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
        else:
            filename = None  # No file uploaded or invalid file type

        # Insert the new shop into the database with the uploaded image filename
        db = connect_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO shops (owner_id, name, address, phone, image, is_approved)
            VALUES (%s, %s, %s, %s, %s, %s)
        """, (session['user_id'], shop_name, address, phone, filename, False))
        db.commit()
        db.close()

        return redirect(url_for('dashboard'))

    return render_template('add_shop.html', translations=translations, lang=language)


# Shop list route (For customers)
@app.route('/shops')
def shop_list():
    db = connect_db()
    cursor = db.cursor()
    # Only fetch shops where is_approved is TRUE
    cursor.execute("SELECT id, name, address, phone, image FROM shops WHERE is_approved = TRUE")
    shops = cursor.fetchall()
    db.close()

    return render_template('shop_list.html', shops=shops)


@app.route('/update_appointment/<int:appointment_id>/<string:status>', methods=['POST'])
def update_appointment(appointment_id, status):
    if 'user_id' not in session or session['role'] != 'shop_owner':
        return redirect(url_for('login'))

    db = connect_db()
    cursor = db.cursor()

    # Update the appointment status
    cursor.execute("""
        UPDATE appointments
        SET status = %s
        WHERE id = %s
    """, (status, appointment_id))
    db.commit()
    db.close()

    return redirect(url_for('dashboard'))


# Route to add services (for shop owners only)
@app.route('/add_service', methods=['GET', 'POST'])
def add_service():
    if 'user_id' not in session or session['role'] != 'shop_owner':
        return redirect(url_for('login'))

    # Load the translations
    language = session.get('lang', 'en')
    translations = load_translation(language)

    if request.method == 'POST':
        service_name = request.form['service_name']
        price = request.form['price']
        duration = request.form['duration']
        shop_id = request.form['shop_id']  # Select shop if shop owner has multiple shops

        db = connect_db()
        cursor = db.cursor()
        cursor.execute("""
            INSERT INTO services (shop_id, service_name, price, duration)
            VALUES (%s, %s, %s, %s)
        """, (shop_id, service_name, price, duration))

        db.commit()
        db.close()
        return redirect(url_for('dashboard'))

    # Get the list of shops owned by the shop owner
    db = connect_db()
    cursor = db.cursor()
    cursor.execute("SELECT id, name FROM shops WHERE owner_id = %s", (session['user_id'],))
    shops = cursor.fetchall()
    db.close()

    return render_template('add_service.html', shops=shops, translations=translations, lang=language)


@app.route('/book/<int:shop_id>', methods=['GET', 'POST'])
def book(shop_id):
    if 'user_id' not in session or session['role'] != 'customer':
        return redirect(url_for('login'))

    db = connect_db()
    cursor = db.cursor()

    if request.method == 'POST':
        # Appointment booking logic
        appointment_date = request.form['appointment_date']
        service_id = request.form['service_id']  # Capture the selected service
        customer_id = session['user_id']

        cursor.execute("""
            INSERT INTO appointments (customer_id, shop_id, appointment_date, status, service_id)
            VALUES (%s, %s, %s, %s, %s)
        """, (customer_id, shop_id, appointment_date, 'pending', service_id))
        db.commit()
        db.close()

        return redirect(url_for('dashboard'))

    # Fetch shop details for displaying in the form
    cursor.execute("SELECT name FROM shops WHERE id = %s", (shop_id,))
    shop_name = cursor.fetchone()[0]

    # Fetch available services for this shop
    cursor.execute("SELECT id, service_name, price FROM services WHERE shop_id = %s", (shop_id,))
    services = cursor.fetchall()  # Get list of services (id, service_name, price)

    db.close()

    # Load translations based on language in session
    language = session.get('lang', 'en')
    translations = load_translation(language)

    return render_template('book_appointment.html', shop_name=shop_name, shop_id=shop_id,
                           services=services, translations=translations, lang=language)


# for photo upload for profile
UPLOAD_FOLDER = 'static/uploads'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


@app.route('/profile', methods=['GET', 'POST'])
def profile():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    user_id = session['user_id']

    db = connect_db()
    cursor = db.cursor()

    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        # Handle profile picture update
        profile_picture = None
        if 'profile_picture' in request.files:
            file = request.files['profile_picture']
            if file and allowed_file(file.filename):
                filename = secure_filename(file.filename)
                file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))
                profile_picture = filename

        # Update the user's profile information
        if password:
            cursor.execute("UPDATE users SET username = %s, email = %s, password = %s WHERE id = %s",
                           (username, email, password, user_id))
        else:
            cursor.execute("UPDATE users SET username = %s, email = %s WHERE id = %s", (username, email, user_id))

        if profile_picture:
            cursor.execute("UPDATE users SET profile_picture = %s WHERE id = %s", (profile_picture, user_id))

        db.commit()
        db.close()

        return redirect(url_for('profile'))

    # Fetch user details from the database
    cursor.execute("SELECT username, email, profile_picture FROM users WHERE id = %s", (user_id,))
    user = cursor.fetchone()
    db.close()

    # Load translations
    language = session.get('lang', 'en')
    translations = load_translation(language)

    return render_template('profile.html', user=user, translations=translations, lang=language)


@app.route('/appointment_history')
def appointment_history():
    if 'user_id' not in session:
        return redirect(url_for('login'))

    language = session.get('lang', 'en')
    translations = load_translation(language)

    db = connect_db()
    cursor = db.cursor()

    # Fetch appointment history for shop owners, grouped by customer, and ordered by the latest date first
    if session['role'] == 'shop_owner':
        cursor.execute("""
            SELECT appointments.appointment_date, appointments.status, users.username, services.service_name, services.price
            FROM appointments
            JOIN users ON appointments.customer_id = users.id
            JOIN services ON appointments.service_id = services.id
            WHERE appointments.shop_id IN (SELECT id FROM shops WHERE owner_id = %s)
            AND appointments.status IN ('confirmed', 'canceled', 'completed')
            ORDER BY appointments.appointment_date DESC, users.username  -- Sort by date (latest first) and then by username
        """, (session['user_id'],))
        history = cursor.fetchall()

        # Group appointments by customer
        customers = {}
        for appointment in history:
            customer_name = appointment[2]
            if customer_name not in customers:
                customers[customer_name] = []
            customers[customer_name].append(appointment)

    else:
        # Fetch appointment history for customers, ordered by the latest date first
        cursor.execute("""
            SELECT appointments.appointment_date, appointments.status, shops.name, services.service_name, services.price
            FROM appointments
            JOIN shops ON appointments.shop_id = shops.id
            JOIN services ON appointments.service_id = services.id
            WHERE appointments.customer_id = %s
            AND appointments.status IN ('confirmed', 'canceled', 'completed')
            ORDER BY appointments.appointment_date DESC  -- Sort by date (latest first)
        """, (session['user_id'],))
        history = cursor.fetchall()
        customers = None  # No need for customer grouping for regular users

    db.close()

    return render_template('appointment_history.html', history=history, customers=customers, translations=translations,
                           lang=language)


# Route for customers to view past appointments
@app.route('/customer_past_appointments')
def customer_past_appointments():
    if 'user_id' not in session or session['role'] != 'customer':
        return redirect(url_for('login'))

    # Load translations based on session language
    language = session.get('lang', 'en')
    translations = load_translation(language)

    db = connect_db()
    cursor = db.cursor()
    current_date = datetime.now()

    # Fetch past appointments for the customer, ordered by the latest date first
    cursor.execute("""
        SELECT appointments.appointment_date, appointments.status, shops.name, services.service_name, services.price
        FROM appointments
        JOIN shops ON appointments.shop_id = shops.id
        JOIN services ON appointments.service_id = services.id
        WHERE appointments.customer_id = %s
        AND appointments.appointment_date < %s
        ORDER BY appointments.appointment_date DESC, shops.name  -- Sort by appointment date in descending order
    """, (session['user_id'], current_date))

    past_appointments = cursor.fetchall()
    db.close()

    return render_template('customer_past_appointments.html', appointments=past_appointments, translations=translations,
                           lang=language)


# Route for customers to view upcoming appointments
@app.route('/customer_upcoming_appointments')
def customer_upcoming_appointments():
    if 'user_id' not in session or session['role'] != 'customer':
        return redirect(url_for('login'))

    db = connect_db()
    cursor = db.cursor()
    current_date = datetime.now()

    # Fetch upcoming appointments for the customer and order them by the earliest date first
    cursor.execute("""
        SELECT appointments.appointment_date, appointments.status, shops.name, services.service_name, services.price
        FROM appointments
        JOIN shops ON appointments.shop_id = shops.id
        JOIN services ON appointments.service_id = services.id
        WHERE appointments.customer_id = %s
        AND appointments.appointment_date >= %s
        ORDER BY appointments.appointment_date ASC  -- This sorts by date in ascending order
    """, (session['user_id'], current_date))

    upcoming_appointments = cursor.fetchall()
    db.close()

    # Load translations
    language = session.get('lang', 'en')
    translations = load_translation(language)

    return render_template('customer_upcoming_appointments.html', appointments=upcoming_appointments,
                           translations=translations, lang=language)


# Route for shop owners to view past appointments
@app.route('/owner_past_appointments')
def owner_past_appointments():
    if 'user_id' not in session or session['role'] != 'shop_owner':
        return redirect(url_for('login'))

    db = connect_db()
    cursor = db.cursor()
    current_date = datetime.now()

    # Fetch past appointments for the shop owner, ordered by the latest date first
    cursor.execute("""
        SELECT appointments.appointment_date, appointments.status, users.username, services.service_name, services.price
        FROM appointments
        JOIN users ON appointments.customer_id = users.id
        JOIN services ON appointments.service_id = services.id
        WHERE appointments.shop_id IN (SELECT id FROM shops WHERE owner_id = %s)
        AND appointments.appointment_date < %s
        ORDER BY appointments.appointment_date DESC, users.username  -- Sort by appointment date in descending order
    """, (session['user_id'], current_date))

    past_appointments = cursor.fetchall()

    # Load translations
    language = session.get('lang', 'en')
    translations = load_translation(language)

    db.close()
    return render_template('owner_past_appointments.html', appointments=past_appointments, translations=translations,
                           lang=language)


# Route for shop owners to view upcoming appointments
@app.route('/owner_upcoming_appointments')
def owner_upcoming_appointments():
    if 'user_id' not in session or session['role'] != 'shop_owner':
        return redirect(url_for('login'))

    db = connect_db()
    cursor = db.cursor()
    current_date = datetime.now()

    # Fetch upcoming appointments for the shop owner, ordered by appointment_date in ascending order
    cursor.execute("""
        SELECT appointments.appointment_date, appointments.status, users.username, services.service_name, services.price
        FROM appointments
        JOIN users ON appointments.customer_id = users.id
        JOIN services ON appointments.service_id = services.id
        WHERE appointments.shop_id IN (SELECT id FROM shops WHERE owner_id = %s)
        AND appointments.appointment_date >= %s
        ORDER BY appointments.appointment_date ASC, users.username
    """, (session['user_id'], current_date))
    upcoming_appointments = cursor.fetchall()

    # Load translations
    language = session.get('lang', 'en')
    translations = load_translation(language)

    db.close()
    return render_template('owner_upcoming_appointments.html', appointments=upcoming_appointments,
                           translations=translations, lang=language)


@app.route('/admin')
def admin():
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    # Get the language from the session or default to 'en'
    language = session.get('lang', 'en')

    # Load the translations
    translations = load_translation(language)

    db = connect_db()
    cursor = db.cursor()

    # Fetch shops that need approval (e.g., shops where is_approved is FALSE)
    cursor.execute("SELECT id, name, address, phone FROM shops WHERE is_approved = FALSE")
    unapproved_shops = cursor.fetchall()

    db.close()

    return render_template('admin_panel.html', translations=translations, lang=language,
                           unapproved_shops=unapproved_shops)


@app.route('/approve_shop/<int:shop_id>', methods=['POST'])
def approve_shop(shop_id):
    if 'user_id' not in session or session['role'] != 'admin':
        return redirect(url_for('login'))

    db = connect_db()
    cursor = db.cursor()

    # Approve the shop by setting is_approved to TRUE
    cursor.execute("UPDATE shops SET is_approved = TRUE WHERE id = %s", (shop_id,))
    db.commit()
    db.close()

    return redirect(url_for('admin'))


# Create database and tables function
def create_database():
    # Establish a connection to MySQL server
    connection = mysql.connector.connect(
        host="localhost",  # Use your MySQL server host
        user="root",  # Your MySQL username
        password=""  # Your MySQL password
    )

    cursor = connection.cursor()

    # Create database if it doesn't exist
    cursor.execute("CREATE DATABASE IF NOT EXISTS salon")

    # Use the salon database
    cursor.execute("USE salon")

    # Create users table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL,
        password VARCHAR(255) NOT NULL,
        email VARCHAR(255) NOT NULL,
        role ENUM('customer', 'shop_owner','admin') NOT NULL
    )
    """)

    # Create shops table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS shops (
        id INT AUTO_INCREMENT PRIMARY KEY,
        owner_id INT,
        name VARCHAR(255) NOT NULL,
        address VARCHAR(255) NOT NULL,
        phone VARCHAR(20),
        FOREIGN KEY (owner_id) REFERENCES users(id)
    )
    """)

    # Create services table
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS services (
        id INT AUTO_INCREMENT PRIMARY KEY,
        shop_id INT,
        service_name VARCHAR(255) NOT NULL,
        price DECIMAL(10, 2) NOT NULL,
        duration INT NOT NULL,  -- Duration in minutes
        FOREIGN KEY (shop_id) REFERENCES shops(id)
    )
    """)

    # Update appointments table to include a reference to the service
    cursor.execute("""
    CREATE TABLE IF NOT EXISTS appointments (
        id INT AUTO_INCREMENT PRIMARY KEY,
        customer_id INT,
        shop_id INT,
        service_id INT,  -- New column to store the booked service
        appointment_date DATETIME NOT NULL,
        status ENUM('pending', 'confirmed', 'canceled') NOT NULL,
        FOREIGN KEY (customer_id) REFERENCES users(id),
        FOREIGN KEY (shop_id) REFERENCES shops(id),
        FOREIGN KEY (service_id) REFERENCES services(id)  -- Link service ID
    )
    """)

    connection.commit()
    cursor.close()
    connection.close()

    print("Database and tables created successfully!")


# Run the Flask app on port 5000
if __name__ == '__main__':
    create_database()
    app.run(debug=True, host="0.0.0.0", port=5000)
