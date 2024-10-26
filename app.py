from flask import Flask, render_template, request, redirect, url_for, flash, session
from datetime import datetime
import json, os


app = Flask(__name__)
app.secret_key = 'your_secret_key'
app.config['JSON_AS_ASCII'] = False

# Data paths
DATA_FILE = 'users.json'
PURCHASE_FILE = 'purchases.json'

# Ensure 'data' directory exists
os.makedirs('data', exist_ok=True)

# Load and save functions for users and purchases
def load_data(file):
    if os.path.exists(file):
        with open(file, 'r') as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print(f"Error reading {file}")
    return []

def save_data(data, file):
    with open(file, 'w') as f:
        json.dump(data, f, indent=4)

# Routes
@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        flash('Post request received!')
        return redirect(url_for('index'))
    return render_template('index.html')
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        # الحصول على بيانات المستخدم من النموذج
        id = request.form['id']
        email = request.form['Email']
        password = request.form['password']

        # تحميل بيانات المستخدمين من ملف JSON
        users = load_data(DATA_FILE)

        # التأكد إذا كان الـ ID أو البريد الإلكتروني مستخدم بالفعل
        if any(user.get('id') == id for user in users):
            flash('ID already exists. Please choose another one.')
            return redirect(url_for('register'))

        if any(user.get('email') == email for user in users):
            flash('Email already exists. Please use another one.')
            return redirect(url_for('register'))

        # إضافة المستخدم الجديد
        users.append({'id': id, 'email': email, 'password': password})
        save_data(users, DATA_FILE)

        # تسجيل المستخدم في الجلسة
        session['id'] = id
        flash(f'Account created successfully for {id}. You are now logged in.')

        # التوجيه إلى الصفحة الرئيسية بعد نجاح التسجيل
        return redirect(url_for('index'))

    return render_template('register.html')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        identifier = request.form['identifier']
        password = request.form['password']

        users = load_data(DATA_FILE)

        user = next((u for u in users if (u['id'] == identifier or u.get('email') == identifier) and u['password'] == password), None)

        if user:
            # تخزين الرقم الجامعي والبريد الإلكتروني في الجلسة
            session['id'] = user['id']
            session['email'] = user['email']
            flash('Logged in successfully!')
            return redirect(url_for('profile'))

        flash('Invalid ID or password.')
        return redirect(url_for('login'))

    return render_template('login.html')

@app.route('/profile')
def profile():
    if 'id' not in session:
        flash('Please log in to view your profile.')
        return redirect(url_for('index'))

    # تمرير البيانات المخزنة في الجلسة إلى القالب
    student_id = session.get('id')
    email = session.get('email')

    return render_template('profile.html', student_id=student_id, email=email)
@app.route('/buy/<book_title>', methods=['POST'])
def buy(book_title):
    if 'id' not in session:
        flash('Please log in to make a purchase.')
        return redirect(url_for('login'))

    student_id = session['id']
    purchase_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')  # تسجيل وقت الشراء

    # حفظ بيانات الشراء
    purchases = load_data(PURCHASE_FILE)
    purchases.append({'id': student_id, 'book_title': book_title, 'purchase_time': purchase_time})
    save_data(purchases, PURCHASE_FILE)

    # إعادة التوجيه لصفحة الفاتورة مع تمرير وقت الشراء كمعامل URL
    return redirect(url_for('invoice', book_title=book_title, purchase_time=purchase_time))


@app.route('/invoice/<book_title>')
def invoice(book_title):
    # الحصول على الرقم الجامعي ووقت الشراء من الجلسة أو الطلب
    student_id = session.get('id')
    purchase_time = request.args.get('purchase_time')  # استلام وقت الشراء من URL

    # قائمة الروابط الخاصة بالكتب
    book_links = {
        'Messages from the Quran': 'https://drive.google.com/file/d/1tvZM_kNWngkJ6lPpVSttO0Kodbgb4xPu/view?usp=sharing',
        'حضارة العرب': 'https://drive.google.com/file/d/2XXXXX/view?usp=sharing',
        # بقية الكتب...
    }

    book_link = book_links.get(book_title, '#')  # استرجاع رابط الكتاب إذا كان موجودًا

    # تمرير الرقم الجامعي، وقت الشراء، والبيانات الأخرى إلى قالب HTML
    return render_template('invoice.html', book_title=book_title, student_id=student_id, book_link=book_link, purchase_time=purchase_time)


    # تمرير الرقم الجامعي، وقت الشراء، والبيانات الأخرى إلى قالب HTML
    return render_template('invoice.html', book_title=book_title, student_id=student_id, book_link=book_link, purchase_time=purchase_time)

@app.route('/my_purchases')
def my_purchases():
    if 'id' not in session:
        flash('Please log in to view your purchases.')
        return redirect(url_for('login'))

    id = session['id']
    purchases = [p for p in load_data(PURCHASE_FILE) if p['id'] == id]
    return render_template('my_purchases.html', purchases=purchases)

@app.route('/about')
def about():
    return render_template('about.html')

if __name__ == '__main__':
    app.run(debug=True)
profile