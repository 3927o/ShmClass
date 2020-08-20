from app import create_app
from app.extensions import db
from app.modules import User

app = create_app("development")
# with app.app_context():
#     db.create_all()
#     app.run(debug=True)
ctx = app.app_context()
ctx.push()
db.create_all()

admin = User("3927", "1624497311@qq.com", "123456", True)
admin.teacher.certificated = True
db.session.add(admin)
db.session.commit()

if __name__ == "__main__":
    app.apscheduler.start()
    app.run(debug=True)
