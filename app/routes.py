from flask import Blueprint, render_template, redirect, url_for, request, flash, session, current_app
from werkzeug.utils import secure_filename
from .models import Product
from .forms import ProductForm
from . import db
import os
import random
main = Blueprint('main', __name__)

# ------------------------- Home Page -------------------------
@main.route('/')
def home():
    products = Product.query.all()
    for p in products:
        print(p.id, p.name, p.image)
    return render_template('home.html', products=products)  # ✅ FIXED

@main.route('/search')
def search_products():
    query = request.args.get('query', '').lower()
    products = Product.query.filter(Product.name.ilike(f'%{query}%')).all()
    return render_template('home.html', products=products, search_query=query)

# ------------------------- Cart -------------------------
@main.route('/add_to_cart/<int:product_id>', methods=['POST'])
def add_to_cart(product_id):
    product = Product.query.get_or_404(product_id)
    cart = session.get('cart', {})

    if str(product_id) in cart:
        cart[str(product_id)]['quantity'] += 1
    else:
        cart[str(product_id)] = {
            'name': product.name,
            'price': product.price,
            'image': product.image,
            'quantity': 1
        }

    session['cart'] = cart
    flash(f"{product.name} added to cart.")
    return redirect(url_for('main.view_cart'))
@main.route('/cart')
def view_cart():
    cart = session.get('cart', {})
    product_ids = list(cart.keys())

    if not product_ids:
        return render_template('cart.html', products=[], total=0)

    products = Product.query.filter(Product.id.in_(product_ids)).all()
    total = sum([cart[str(p.id)]['quantity'] * p.price for p in products])
    return render_template('cart.html', products=products, cart=cart, total=total)
@main.route('/remove_from_cart/<int:product_id>', methods=['POST'])
def remove_from_cart(product_id):
    cart = session.get('cart', {})
    if str(product_id) in cart:
        del cart[str(product_id)]
        session['cart'] = cart
        flash('Item removed from cart.')
    return redirect(url_for('main.view_cart'))


@main.route('/checkout')
def checkout():
    cart = session.get('cart', {})
    total = sum(item['price'] * item['quantity'] for item in cart.values())
    return render_template('checkout.html', cart=cart, total=total)

# ------------------------- Admin Login -------------------------
@main.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        if username == 'admin' and password == 'admin123':
            session['admin_logged_in'] = True
            flash('Logged in successfully!', 'success')
            return redirect(url_for('main.admin_view_products'))
        else:
            flash('Invalid credentials', 'danger')
    return render_template('admin_login.html')

@main.route('/admin/logout')
def admin_logout():
    session.pop('admin_logged_in', None)
    flash('Logged out successfully!', 'success')
    return redirect(url_for('main.home'))


# ------------------------- Admin: View All Products -------------------------
@main.route('/admin/view-products')
def admin_view_products():
    if not session.get('admin_logged_in'):
        return redirect(url_for('main.admin_login'))
    products = Product.query.all()
    return render_template('admin_manage.html', products=products)


# ------------------------- Admin: Add Product -------------------------
@main.route('/admin/add-product', methods=['GET', 'POST'])
def admin_add_product():
    form = ProductForm()
    if form.validate_on_submit():
        print("✅ Form submitted successfully")

        # Save image
        image_folder = os.path.join(current_app.root_path, 'static', 'product_images')
        os.makedirs(image_folder, exist_ok=True)

        filename = secure_filename(form.image.data.filename)
        image_path = os.path.join(image_folder, filename)
        form.image.data.save(image_path)

        # Save product to DB
        product = Product(
            name=form.name.data,
            description=form.description.data,
            price=form.price.data,
            category=form.category.data,
            image=f'product_images/{filename}'
        )
        db.session.add(product)
        db.session.commit()

        flash("Product added successfully!", "success")
        return redirect(url_for('main.admin_view_products'))  # ✅ Go to manage page

    # 🛑 Add this to debug why it failed
    if request.method == 'POST':
        print("❌ Form failed:", form.errors)

    return render_template('admin_add_product.html', form=form)


# ------------------------- Category Page -------------------------
@main.route('/category/<category>')
def view_category(category):
    products = Product.query.filter_by(category=category).all()
    for product in products:
        print(product.name, product.description, product.price)  # Debug
    return render_template('category.html', products=products, category=category)

# ------------------------- Admin: Delete Product -------------------------
@main.route('/admin/delete/<int:product_id>', methods=['POST'])
def admin_delete_product(product_id):
    if not session.get('admin_logged_in'):
        flash('Access denied. Please log in.', 'danger')
        return redirect(url_for('main.admin_login'))

    product = Product.query.get_or_404(product_id)
    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully!', 'success')
    return redirect(url_for('main.admin_view_products'))
@main.route('/cart')
def cart():
    cart = session.get('cart', [])
    products = Product.query.filter(Product.id.in_(cart)).all() if cart else []
  # Replace with your actual logic
    return render_template('category.html', products=products, show_delete=False, page_title='My Cart')

@main.route('/accessories')
def accessories():
    products = Product.query.filter_by(category='Accessories').all()
    return render_template('category.html', products=products, show_delete=False, page_title='Accessories')

@main.route('/shoes')
def shoes():
    products = Product.query.filter_by(category='Shoes').all()
    return render_template('category.html', products=products, show_delete=False, page_title='Shoes')

@main.route('/clothes')
def clothes():
    products = Product.query.filter_by(category='Clothing').all()  # ← change 'Clothes' to 'Clothing'
    return render_template('category.html', products=products, show_delete=False, page_title='Clothing')

@main.route('/electronics')
def electronics():
    products = Product.query.filter_by(category='Electronics').all()
    return render_template('category.html', products=products, show_delete=False, page_title='Electronics')
@main.route('/place_order', methods=['POST'])
def place_order():
    cart = session.get('cart', {})
    if not cart:
        flash("Your cart is empty.")
        return redirect(url_for('main.view_cart'))

    # Calculate total
    total = sum(item['price'] * item['quantity'] for item in cart.values())

    # Generate fake order ID
    order_id = f"ORD{random.randint(100000, 999999)}"

    # Clear cart
    session['cart'] = {}
    return render_template('order_confirmation.html', order_id=order_id, total=total)