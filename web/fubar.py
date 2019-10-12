from init import app
from init import db

@app.route('/')
def welcome():
    return "Welcome to Fubar!"

if __name__ == "__main__":
    db.create_all()
    app.run()