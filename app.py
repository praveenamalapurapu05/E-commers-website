from flask import Flask, render_template, request, redirect, url_for, flash, session
from flask_sqlalchemy import SQLAlchemy


# ==========================================
# FLASK APPLICATION
# ==========================================

app = Flask(__name__)

app.secret_key = "praveen-store-secret-key"

# Database configuration
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///praveen_store.db"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db = SQLAlchemy(app)


# ==========================================
# PRODUCT DATABASE MODEL
# ==========================================

class Product(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(db.String(100), nullable=False)

    price = db.Column(db.Float, nullable=False)

    emoji = db.Column(db.String(10), nullable=False)

    description = db.Column(db.Text, nullable=False)

    stock = db.Column(db.Integer, default=10)
# ==========================================
# ORDER DATABASE MODEL
# ==========================================

class Order(db.Model):

    id = db.Column(db.Integer, primary_key=True)

    customer_name = db.Column(
        db.String(100),
        nullable=False
    )

    customer_email = db.Column(
        db.String(120),
        nullable=False
    )

    customer_phone = db.Column(
        db.String(20),
        nullable=False
    )

    customer_address = db.Column(
        db.Text,
        nullable=False
    )

    total_amount = db.Column(
        db.Float,
        nullable=False
    )

    status = db.Column(
        db.String(30),
        default="Pending"
    )

# ==========================================
# ORDER ITEM DATABASE MODEL
# ==========================================

class OrderItem(db.Model):

    id = db.Column(
        db.Integer,
        primary_key=True
    )

    order_id = db.Column(
        db.Integer,
        db.ForeignKey("order.id"),
        nullable=False
    )

    product_id = db.Column(
        db.Integer,
        nullable=False
    )

    product_name = db.Column(
        db.String(100),
        nullable=False
    )

    price = db.Column(
        db.Float,
        nullable=False
    )

    quantity = db.Column(
        db.Integer,
        nullable=False
    )

    subtotal = db.Column(
        db.Float,
        nullable=False
    )
# ==========================================
# CREATE DATABASE + DEFAULT PRODUCTS
# ==========================================

with app.app_context():

    db.create_all()

    if Product.query.count() == 0:

        products = [

            Product(
                name="Laptop",
                price=55000,
                emoji="💻",
                description="Powerful laptop for work, study and entertainment.",
                stock=10
            ),

            Product(
                name="Smartphone",
                price=25000,
                emoji="📱",
                description="Modern smartphone with powerful features.",
                stock=15
            ),

            Product(
                name="Headphones",
                price=2500,
                emoji="🎧",
                description="Enjoy clear and immersive sound anywhere.",
                stock=20
            ),

            Product(
                name="Smart Watch",
                price=4000,
                emoji="⌚",
                description="Track your fitness and stay connected.",
                stock=12
            )

        ]

        db.session.add_all(products)
        db.session.commit()


# ==========================================
# HOME PAGE
# ==========================================

@app.route("/")
def home():

    products = Product.query.all()

    cart = session.get("cart", {})

    cart_count = sum(cart.values())

    return render_template(
        "index.html",
        products=products,
        cart_count=cart_count
    )


# ==========================================
# PRODUCTS PAGE
# ==========================================

@app.route("/products")
def products():

    product_list = Product.query.all()

    cart = session.get("cart", {})

    cart_count = sum(cart.values())

    return render_template(
        "index.html",
        products=product_list,
        cart_count=cart_count
    )


# ==========================================
# ADD PRODUCT TO CART
# ==========================================

@app.route("/add-to-cart/<int:product_id>")
def add_to_cart(product_id):

    product = db.session.get(Product, product_id)

    if product is None:

        flash("Product not found.", "error")

        return redirect(url_for("home"))

    if product.stock <= 0:

        flash(
            f"{product.name} is currently out of stock.",
            "error"
        )

        return redirect(url_for("home"))

    cart = session.get("cart", {})

    product_id = str(product_id)

    current_quantity = cart.get(product_id, 0)

    if current_quantity >= product.stock:

        flash(
            f"Only {product.stock} units of {product.name} are available.",
            "error"
        )

        return redirect(url_for("home"))

    cart[product_id] = current_quantity + 1

    session["cart"] = cart

    flash(
        f"{product.name} added to your cart! 🛒",
        "success"
    )

    return redirect(url_for("home"))


# ==========================================
# CART PAGE
# ==========================================

@app.route("/cart")
def cart():

    cart = session.get("cart", {})

    cart_products = []

    total = 0

    cart_count = sum(cart.values())

    for product_id, quantity in cart.items():

        product = db.session.get(
            Product,
            int(product_id)
        )

        if product:

            subtotal = product.price * quantity

            cart_products.append({
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal
            })

            total += subtotal

    return render_template(
        "cart.html",
        cart_products=cart_products,
        total=total,
        cart_count=cart_count
    )

# ==========================================
# CHECKOUT PAGE
# ==========================================

@app.route("/checkout")
def checkout():

    cart = session.get("cart", {})

    if not cart:

        flash(
            "Your cart is empty.",
            "error"
        )

        return redirect(url_for("home"))

    cart_products = []

    total = 0

    cart_count = sum(cart.values())

    for product_id, quantity in cart.items():

        product = db.session.get(
            Product,
            int(product_id)
        )

        if product:

            subtotal = product.price * quantity

            cart_products.append({
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal
            })

            total += subtotal

    return render_template(
        "checkout.html",
        cart_products=cart_products,
        total=total,
        cart_count=cart_count
    )

# ==========================================
# PLACE ORDER
# ==========================================

@app.route("/place-order", methods=["POST"])
def place_order():

    cart = session.get("cart", {})

    if not cart:

        flash(
            "Your cart is empty.",
            "error"
        )

        return redirect(url_for("home"))

    customer_name = request.form.get("customer_name")
    customer_email = request.form.get("customer_email")
    customer_phone = request.form.get("customer_phone")
    customer_address = request.form.get("customer_address")

    total = 0

    cart_items = []

    # Calculate total and collect products

    for product_id, quantity in cart.items():

        product = db.session.get(
            Product,
            int(product_id)
        )

        if product:

            subtotal = product.price * quantity

            total += subtotal

            cart_items.append({
                "product": product,
                "quantity": quantity,
                "subtotal": subtotal
            })


    # Create the main order

    order = Order(
        customer_name=customer_name,
        customer_email=customer_email,
        customer_phone=customer_phone,
        customer_address=customer_address,
        total_amount=total,
        status="Pending"
    )

    db.session.add(order)

    db.session.flush()


    # Create order items

    for item in cart_items:

        order_item = OrderItem(
            order_id=order.id,
            product_id=item["product"].id,
            product_name=item["product"].name,
            price=item["product"].price,
            quantity=item["quantity"],
            subtotal=item["subtotal"]
        )

        db.session.add(order_item)


    # Save everything

    db.session.commit()


    # Clear cart

    session.pop("cart", None)


    # Go to confirmation page

    return redirect(
        url_for(
            "order_confirmation",
            order_id=order.id
        )
    )

# ==========================================
# ORDER CONFIRMATION
# ==========================================

@app.route("/order-confirmation/<int:order_id>")
def order_confirmation(order_id):

    order = db.session.get(
        Order,
        order_id
    )

    if order is None:

        flash(
            "Order not found.",
            "error"
        )

        return redirect(url_for("home"))

    order_items = OrderItem.query.filter_by(
        order_id=order.id
    ).all()

    return render_template(
        "order_confirmation.html",
        order=order,
        order_items=order_items
    )
# ==========================================
# INCREASE QUANTITY
# ==========================================

@app.route("/cart/increase/<int:product_id>")
def increase_quantity(product_id):

    product = db.session.get(Product, product_id)

    if product is None:

        flash("Product not found.", "error")

        return redirect(url_for("cart"))

    cart = session.get("cart", {})

    product_id = str(product_id)

    current_quantity = cart.get(product_id, 0)

    if current_quantity < product.stock:

        cart[product_id] = current_quantity + 1

        session["cart"] = cart

    else:

        flash(
            f"Only {product.stock} units available.",
            "error"
        )

    return redirect(url_for("cart"))


# ==========================================
# DECREASE QUANTITY
# ==========================================

@app.route("/cart/decrease/<int:product_id>")
def decrease_quantity(product_id):

    cart = session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:

        if cart[product_id] > 1:

            cart[product_id] -= 1

        else:

            del cart[product_id]

        session["cart"] = cart

    return redirect(url_for("cart"))


# ==========================================
# REMOVE PRODUCT
# ==========================================

@app.route("/cart/remove/<int:product_id>")
def remove_from_cart(product_id):

    cart = session.get("cart", {})

    product_id = str(product_id)

    if product_id in cart:

        del cart[product_id]

        session["cart"] = cart

        flash(
            "Product removed from your cart.",
            "success"
        )

    return redirect(url_for("cart"))


# ==========================================
# 404 ERROR
# ==========================================

@app.errorhandler(404)
def page_not_found(error):

    return render_template(
        "index.html",
        products=Product.query.all(),
        cart_count=sum(
            session.get("cart", {}).values()
        )
    ), 404


# ==========================================
# RUN APPLICATION
# ==========================================

if __name__ == "__main__":

    app.run(debug=True)