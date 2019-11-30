from flask import Flask, render_template      

app = Flask(__name__)

@app.route("/")
def home():
    return render_template("index.html")

@app.route("/login/:phone")
    return 

@app.route("/salvador")
def salvador():
    return "Hello, Salvadorrrr"
    
if __name__ == "__main__":
    app.run(debug=True)