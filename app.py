from flask import Flask 
app = Flask(__name__)
@app.route("/")
<<<<<<< HEAD

def home():
  return "Welcome to the X-Bix TechVentures Issue & Vulnerability Tracking API"

if __name__ == "__main__":
    app.run(debug=True)
=======
>>>>>>> 81858a6 (Updated Flask app and dependencies; added gitignore for venv)

def home():

    return "Welcome to the X-Bix TechVentures Issue & Vulnerability Tracking API"

if __name__ == "__main__":
    app.run(debug=True)
