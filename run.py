from app import create_app
from app.extensions import db

app = create_app("development")
# with app.app_context():
#     db.create_all()
#     app.run(debug=True)
ctx = app.app_context()
ctx.push()
db.create_all()

if __name__ == "__main__":
    app.apscheduler.start()
    app.run(debug=True)
