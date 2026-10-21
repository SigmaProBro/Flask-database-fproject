from flask import Flask, render_template, request, redirect, url_for, session
from flask_sqlalchemy import SQLAlchemy
from database import SessionLocal, User, Food, Booking
import hashlib
from datetime import datetime
import os
from werkzeug.utils import secure_filename

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///skills.db'
app.config['SECRET_KEY'] = 'secret'
db = SQLAlchemy(app)


with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html')


@app.route('/menu')
def menu():
    with SessionLocal() as db:
        foods = db.query(Food).all()
        return render_template('menu.html', foods=foods)



    
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        with SessionLocal() as db:
            username = request.form['username']
            email = request.form['email']

            if db.query(User).filter_by(username=username).first():
                return 'Такий нік вже зайнятий!'

            if db.query(User).filter_by(email=email).first():
                return 'Ця пошта вже зареєстрована!'

            user = User(
                username=username,
                password=hashlib.sha256(
                    request.form['password'].encode()).hexdigest(),
                email=email
            )

            db.add(user)
            db.commit()

            session['user_id'] = user.id
            session['is_admin'] = user.username == "vlad"

        return redirect(url_for('index'))

    return render_template('register.html')


@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        with SessionLocal() as db:
            user = db.query(User).filter_by(
                username=username,
                password=hashlib.sha256(password.encode()).hexdigest()
            ).first()

            if user:
                session['user_id'] = user.id
                session['is_admin'] = user.username == "vlad"
                return redirect(url_for('index'))

            return 'Неправильний логін або пароль'

    return render_template('login.html')

@app.route('/position/<name>', methods=['GET', 'POST'])
def position(name):
    with SessionLocal() as db:
        food = db.query(Food).filter_by(name=name).first()

        if not food:
            return 'Страву не знайдено', 404

        if request.method == 'POST':
            cart = session.get('cart', {})
            food_id = str(food.id)
            
            if sum(cart.values()) < 10:
                cart[food_id] = cart.get(food_id, 0) + 1
            
            session['cart'] = cart
            
            

            session['cart'] = cart

            return redirect(url_for('position', name=food.name))

        return render_template('position.html', food=food)

@app.route('/admin')
def admin():
    if not session.get('is_admin'):
        return 'Доступ заборонено!', 403

    return render_template('admin.html')


@app.route('/admin/add_food', methods=['GET', 'POST'])
def add_food():
    if not session.get('is_admin'):
        return 'Доступ заборонено!', 403

    if request.method == 'POST':
        name = request.form['name']
        price = float(request.form['price'])
        description = request.form['description']
        ingredients = request.form['ingredients']
        weight = int(request.form['weight'])
        file = request.files['image']

        if file and file.filename:
            filename = secure_filename(file.filename)
            os.makedirs('static/img', exist_ok=True)
            file.save(os.path.join('static/img', filename))

            with SessionLocal() as db:
                food = Food(
                    name=name,
                    price=price,
                    image='img/' + filename,
                    description=description,
                    ingredients=ingredients,
                    weight=weight
                )

                db.add(food)
                db.commit()

            return redirect(url_for('admin'))

    return render_template('add_food.html')


@app.route('/admin/delete_food/<int:food_id>', methods=['POST'])
def delete_food(food_id):
    if not session.get('is_admin'):
        return 'Доступ заборонено!', 403

    with SessionLocal() as db:
        food = db.get(Food, food_id)

        if not food:
            return 'Страву не знайдено', 404

        db.delete(food)
        db.commit()

    return redirect(url_for('menu'))

@app.route('/admin/edit_price', methods=['GET', 'POST'])
def edit_price():
    return 'Функція редагування ціни ще не реалізована'

@app.route('/cart', methods=['GET', 'POST'])
def cart():
    cart = session.get('cart', {})

    if request.method == 'POST':
        food_id = request.form['food_id']
        cart.pop(food_id, None)
        session['cart'] = cart
        return redirect(url_for('cart'))

    foods = []
    total = 0

    with SessionLocal() as db:
        for food_id, quantity in cart.items():
            food = db.get(Food, int(food_id))

            if food:
                price = food.price * quantity
                foods.append({
                    'food': food,
                    'quantity': quantity,
                    'sum': price
                })
                total += price

    return render_template('cart.html', foods=foods, total=total)


@app.route('/logout')
def logout():
    session.pop('user_id', None)
    session.pop('is_admin', None)
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)