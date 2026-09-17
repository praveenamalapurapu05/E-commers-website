from flask import Flask, render_template, request, redirect, url_for, flash

app = Flask(__name__)

# Secret key is required for flash messages
app.secret_key = "praveen-store-secret-key"


# Product data
products = [
    {
        "name": "Laptop",
        "price": 55000,
        "emoji": "💻",
        "description": "Powerful laptop for work, study and entertainment."
    },
    {
        "name": "Smartphone",
        "price": 25000,
        "emoji": "📱",
        "description": "Modern smartphone with powerful features."
    },
    {
        "name": "Headphones",
        "price": 2500,
        "emoji": "🎧",
        "description": "Enjoy clear and immersive sound anywhere."
    },
    {
        "name": "Smart Watch",
        "price": 4000,
        "emoji": "⌚",
        "description": "Track your fitness and stay connected."
    }
]


# Home page
@app.route("/")
def home():
    return render_template("index.html", products=products)


# Products page
@app.route("/products")
def product_page():
    return render_template("index.html", products=products)


# Add product to cart
@app.route("/add-to-cart/<product_name>", methods=["POST"])
def add_to_cart(product_name):

    selected_product = None

    for product in products:
        if product["name"] == product_name:
            selected_product = product
            break

    if selected_product:
        flash(
            f"{selected_product['name']} has been added to your cart! 🛒",
            "success"
        )
    else:
        flash("Product not found.", "error")

    return redirect(url_for("home"))


# Error handling - Page not found
@app.errorhandler(404)
def page_not_found(error):
    return """
    <h1>404 - Page Not Found</h1>
    <p>The page you are looking for does not exist.</p>
    <a href="/">Go back to Praveen Store</a>
    """, 404


# Error handling - Internal server error
@app.errorhandler(500)
def internal_server_error(error):
    return """
    <h1>500 - Server Error</h1>
    <p>Something went wrong. Please try again later.</p>
    <a href="/">Go back to Praveen Store</a>
    """, 500


# Run application
if __name__ == "__main__":
    app.run(debug=True)