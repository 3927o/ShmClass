import logging
from app import create_app
from app.extensions import db
from app.modules import User, Course, Media


app = create_app("development")
# with app.app_context():
#     db.create_all()
#     app.run(debug=True)
ctx = app.app_context()
ctx.push()
db.create_all()

from app.scheduler import task_remind_job

admin = User("3927", "1624497311@qq.com", "123456", True)
customer = User("lin", "2900303329@qq.com", "123456")
course1 = Course("first class", 1, 1, 0, 2598185537, "welcome")
to_del_course = Course("deleted course", 1, 1, 0, 2598185537)
test_media = Media('/test.jpg', "1", "test_media")
admin.teacher.certificated = True
db.session.add(admin)
db.session.add(customer)
db.session.add(course1)
db.session.add(to_del_course)
db.session.add(test_media)
db.session.commit()

fh = logging.FileHandler('log.log')
fh.setLevel(logging.DEBUG)
app.logger.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s - %(message)s')
fh.setFormatter(formatter)
app.logger.addHandler(fh)

if __name__ == "__main__":
    app.apscheduler.start()
    app.run(debug=True)
