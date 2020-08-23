from app import create_app
from app.extensions import db
from app.modules import User, Course

app = create_app("development")
# with app.app_context():
#     db.create_all()
#     app.run(debug=True)
ctx = app.app_context()
ctx.push()
db.create_all()

admin = User("3927", "1624497311@qq.com", "123456", True)
customer = User("lin", "2900303329@qq.com", "123456")
course1 = Course("first class", 1, 1, 0, 2598185537, "welcome")
admin.teacher.certificated = True
db.session.add(admin)
db.session.add(customer)
db.session.add(course1)
db.session.commit()

if __name__ == "__main__":
    app.apscheduler.start()
    app.run(debug=True)
