from flask import Flask, render_template

app = Flask(__name__)

products = [
    {
        "name": "Laptop",
        "price": 55000,
        "emoji": "💻"
    },
    {
        "name": "Smartphone",
        "price": 25000,
        "emoji": "📱"
    },
    {
        "name": "Headphones",
        "price": 2500,
        "emoji": "🎧"
    },
    {
        "name": "Smart Watch",
        "price": 4000,
        "emoji": "⌚"
    }
]


@app.route("/")
def home():
    return "Hello! My E-commers Website is Working"

if __name__ == "__main__":
    app.run(debug=True)