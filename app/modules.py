import redis
import pickle
import random
import os
from math import ceil
from uuid import uuid4 as uuid
from time import time

from werkzeug.security import generate_password_hash, check_password_hash
from flask import url_for, request, current_app, g

from app.extensions import db, pool
from app.helpers import guess_type, format_time


r = redis.Redis(connection_pool=pool)


def uuid4():
    return str(uuid())


assist_table = db.Table('association1',
                        db.Column('course_id', db.Integer, db.ForeignKey('course.id')),
                        db.Column('student_id', db.Integer, db.ForeignKey('student.sid')))

user_task = db.Table('association2',
                     db.Column('task_id', db.Integer, db.ForeignKey('task.id')),
                     db.Column('student_id', db.Integer, db.ForeignKey('student.sid')))


class User(db.Model):
    id_name = 'uid'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True, index=True)
    nickname = db.Column(db.String(18), nullable=False, unique=True)
    name = db.Column(db.String(18))
    introduce = db.Column(db.String(300))
    avatar = db.Column(db.String(36))
    school = db.Column(db.String(30))
    email = db.Column(db.String(50), unique=True, nullable=False)
    gender = db.Column(db.Enum('male', 'female', 'secret'), default='secret')
    telephone = db.Column(db.String(11), unique=True)
    password_hash = db.Column(db.String(128))
    admin = db.Column(db.Boolean, default=False)
    create_at = db.Column(db.Float, nullable=False, default=time)
    update_at = db.Column(db.Float, default=time, onupdate=time)

    comments = db.relationship("Comment", back_populates="author", cascade="all")
    discussions = db.relationship("Discussion", back_populates="master", cascade="all")

    student = db.relationship("Student", back_populates="user", cascade="all", uselist=False)
    teacher = db.relationship("Teacher", back_populates="user", cascade="all", uselist=False)

    def __init__(self, nickname, email, password, admin=False):
        self.nickname = nickname
        self.name = nickname
        self.avatar = Media.random_avatar()
        self.email = email
        self.set_password(password)
        self.admin = admin
        self.student = Student()
        self.teacher = Teacher()

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def validate_password(self, password):
        return check_password_hash(self.password_hash, password)

    def is_teacher(self, course):
        return course.teacher == self.teacher
    
    def is_student(self, course):
        return self.student in course.students

    def to_json(self, detail=False):
        data = {
            "self": request.host_url[0:-1] + url_for('student_bp.info', uid=self.id),
            "uid": self.id,
            "avatar": Media.load_media_from_uuid(self.avatar, return_model=True).url if self.avatar is not None else None,
            "nickname": self.nickname,
            "introduce": self.introduce,
            "gender": self.gender,
            "school": self.school
        }

        if detail:
            data_detail = {
                "name": self.name,
                "telephone": self.telephone,
                "email": self.email,
            }
            data.update(data_detail)

        return data

    @staticmethod
    def list_to_json(users):
        data = {
            "count": len(users),
            "items": [user.to_json() for user in users]
        }
        return data

    def like(self, resource_id, resource_type):
        prefix = "like_{}:".format(resource_type)
        key = prefix + resource_id
        r.sadd(key, self.id)

    def liked(self, resource_id, resource_type):
        prefix = "like_{}:".format(resource_type)
        key = prefix + resource_id
        return r.sismember(key, self.id)

    def collect(self, resource_id, resource_type):
        prefix = "collect_{}:".format(resource_type)
        user_collect_key = "user:{}:collect_{}".format(self.id, resource_type)
        key = prefix + resource_id
        r.sadd(key, self.id)
        r.sadd(user_collect_key, resource_id)

    def collected(self, resource_id, resource_type):
        prefix = "collect_{}:".format(resource_type)
        key = prefix + resource_id
        return r.sismember(key, self.id)
    
    def judge_role(self, course):
        if self.is_teacher(course):
            role = "teacher"
        elif self.is_student(course):
            role = "student"
        else:
            role = "customer"
        
        return role


class Student(db.Model):
    student_id = db.Column(db.String(30))
    grade = db.Column(db.String(18))
    class_ = db.Column(db.String(18))
    id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)
    sid = db.Column(db.Integer, primary_key=True, autoincrement=True)

    user = db.relationship("User", back_populates="student")
    courses = db.relationship("Course", back_populates='students', secondary=assist_table)
    tasks = db.relationship("Task", back_populates='students', secondary=user_task)
    answers = db.relationship("TaskAnswer", back_populates='student', cascade='all')
    prob_answers = db.relationship("Answer", back_populates='student', cascade='all')

    def __init__(self):
        pass

    def to_json(self, detail=False):
        user = self.user
        data = {
            "self": request.host_url[0:-1] + url_for('student_bp.info', uid=self.id),
            "uid": user.id,
            "avatar": Media.load_media_from_uuid(user.avatar, return_model=True).url if user.avatar is not None else None,
            "nickname": user.nickname,
            "introduce": user.introduce,
            "gender": user.gender,
            "school": user.school,
        }

        if detail:
            data_detail = {
                "name": user.name,
                "student_id": self.student_id,
                "telephone": user.telephone,
                "grade": self.grade,
                "class": self.class_,
                "email": user.email,
            }
            data.update(data_detail)

        return data

    @staticmethod
    def list_to_json(students):
        data = {
            "count": len(students),
            "items": [student.to_json() for student in students]
        }
        return data


class Teacher(db.Model):
    teacher_id = db.Column(db.String(30))
    id = db.Column(db.Integer, db.ForeignKey("user.id"), index=True)
    tid = db.Column(db.Integer, primary_key=True, autoincrement=True)
    certificated = db.Column(db.Boolean, default=False)

    user = db.relationship("User", back_populates="teacher")
    courses = db.relationship("Course", back_populates='teacher', cascade='all')
    tasks = db.relationship("Task", back_populates='teacher', cascade='all')

    def __init__(self):
        pass

    def to_json(self, detail=False):
        user = self.user
        data = {
            "self": request.host_url[0:-1] + url_for('teacher_bp.info', uid=self.id),
            "uid": self.id,
            "avatar": Media.load_media_from_uuid(user.avatar, return_model=True).url if user.avatar is not None else None,
            "introduce": user.introduce,
            "gender": user.gender,
            "name": user.name,
            "school": user.school,
        }

        if detail:
            data_detail = {
                "telephone": user.telephone,
                "email": user.email,
                "teacher_id": self.teacher_id
            }
            data.update(data_detail)

        return data


class Course(db.Model):
    id_name = "cid"

    id = db.Column(db.Integer, autoincrement=True, index=True, primary_key=True)
    name = db.Column(db.String(36), nullable=False)
    introduce = db.Column(db.String(100))
    public = db.Column(db.Boolean, nullable=False, index=True)
    avatar = db.Column(db.String(36))
    start_at = db.Column(db.Float, nullable=False)
    end_at = db.Column(db.Float, nullable=False)
    create_at = db.Column(db.Float, nullable=False, default=time)
    update_at = db.Column(db.Float, default=time, onupdate=time)

    chapters = db.relationship("Chapter", back_populates='course', cascade='all')
    tasks = db.relationship("Task", back_populates='course', cascade='all')
    students = db.relationship("Student", back_populates='courses', secondary=assist_table)
    discussions = db.relationship("Discussion", back_populates="course", cascade="all")
    notices = db.relationship("Notice", back_populates='course', cascade='all')

    teacher_id = db.Column(db.Integer, db.ForeignKey("teacher.tid"))
    teacher = db.relationship("Teacher", back_populates="courses")

    def __init__(self, name, public, teacher_id, start_at, end_at, introduce=None):
        self.name = name
        self.public = public
        self.teacher_id = teacher_id
        self.start_at = start_at
        self.end_at = end_at
        if introduce is not None:
            self.introduce = introduce

    def to_json(self, detail=False):
        data = {
            "self": request.host_url[0:-1] + url_for('course_bp.course', cid=self.id),
            "id": self.id,
            "name": self.name,
            "avatar": Media.load_media_from_uuid(self.avatar, return_model=True).url if self.avatar is not None else None,
            "introduce": self.introduce,
            "public": self.public,
            "create_status": 1 if g.current_user.teacher == self.teacher else 0,
            "join_status": 1 if self in g.current_user.student.courses else 0,
            "start_at": format_time(self.start_at),
            "end_at": format_time(self.end_at),
            "time_excess": not self.start_at <= time() <= self.end_at,
            "teacher_name": self.teacher.user.name if self.teacher.user.name is not None else self.teacher.user.nickname
        }
        if detail:
            data_detail = {
                "teacher": self.teacher.to_json(detail=False)
            }
            data.update(data_detail)
        return data

    def to_json_as_student(self):
        data = {
            "self": request.host_url[0:-1] + url_for('course_bp.course', cid=self.id),
            "id": self.id,
            "name": self.name,
            "avatar": Media.load_media_from_uuid(self.avatar, return_model=True).url if self.avatar is not None else None,
            "introduce": self.introduce,
            "public": self.public,
            "start_at": format_time(self.start_at),
            "end_at": format_time(self.end_at),
            "time_excess": not self.start_at <= time() <= self.end_at,
            "teacher": self.teacher.to_json(detail=False)
        }
        return data

    def to_json_as_teacher(self):
        data = {
            "self": request.host_url[0:-1] + url_for('course_bp.course', cid=self.id),
            "id": self.id,
            "name": self.name,
            "avatar": Media.load_media_from_uuid(self.avatar, return_model=True).url if self.avatar is not None else None,
            "introduce": self.introduce,
            "public": self.public,
            "start_at": format_time(self.start_at),
            "end_at": format_time(self.end_at),
            "time_excess": not self.start_at <= time() <= self.end_at
        }
        return data

    @classmethod
    def list_to_json(cls, courses, type_="course"):
        bp_map = {"teacher": "teacher_bp", "student": "student_bp", "course": "course_bp"}
        schema_map = {"teacher": cls.to_json_as_teacher, "student": cls.to_json_as_student, "course": cls.to_json}
        bp_name = bp_map[type_]
        schema = schema_map[type_]
        data = {
            "self": request.host_url[0:-1] + url_for(bp_name + ".courses"),
            "count": len(courses),
            "courses": [schema(course) for course in courses]
        }
        return data


class Chapter(db.Model):
    id_name = "chapter_id"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, index=True)
    name = db.Column(db.String)
    documents = db.Column(db.Text)
    movies = db.Column(db.Text)
    create_at = db.Column(db.Float, default=time)
    update_at = db.Column(db.Float, default=time, onupdate=time)

    course_id = db.Column(db.Integer, db.ForeignKey("course.id"))
    course = db.relationship("Course", back_populates='chapters')

    def __init__(self, name, documents=None, movies=None):
        self.name = name
        self.movies = pickle.dumps([]) if movies is None else movies
        self.documents = pickle.dumps([]) if documents is None else documents

    def to_json(self, with_documents=False, with_movies=False):
        data = {
            "id": self.id,
            "name": self.name,
            "create_at": format_time(self.create_at),
            "update_at": format_time(self.update_at)
        }
        data_documents = {
            "document_count": len(pickle.loads(self.documents)) if self.documents is not None else 0,
            "documents": Media.load_medias_from_uuid_list(pickle.loads(self.documents)) if self.documents is not None else None
        }
        data_movies = {
            "movie_count": len(pickle.loads(self.movies)) if self.movies is not None else 0,
            "movies": Media.load_medias_from_uuid_list(pickle.loads(self.movies)) if self.movies is not None else None
        }
        data.update(data_documents) if with_documents else 1  # else pass
        data.update(data_movies) if with_movies else 1
        return data

    @staticmethod
    def list_to_json(chapters, with_documents=False, with_movies=False):
        data = {
            "count": len(chapters),
            "chapters": [chapter.to_json(with_documents, with_movies) for chapter in chapters]
        }
        return data


class Task(db.Model):
    id_name = "tid"

    id = db.Column(db.String(36), primary_key=True, index=True, default=uuid4)
    type = db.Column(db.Enum('exam', 'test'))
    name = db.Column(db.String(18))
    introduce = db.Column(db.Text)
    answer_visible = db.Column(db.Boolean)
    max_score = db.Column(db.Integer)
    create_at = db.Column(db.Float, default=time)
    time_begin = db.Column(db.Float, default=time)
    time_end = db.Column(db.Float, nullable=False)
    expires = db.Column(db.Float)

    answers = db.relationship("TaskAnswer", back_populates='task', cascade='all')
    problems = db.relationship("Problem", back_populates='task', cascade='all')
    students = db.relationship("Student", back_populates='tasks', secondary=user_task)

    course_id = db.Column(db.Integer, db.ForeignKey('course.id'))
    course = db.relationship("Course", back_populates='tasks')

    teacher_id = db.Column(db.Integer, db.ForeignKey("teacher.tid"))
    teacher = db.relationship("Teacher", back_populates="tasks")

    def __init__(self, type_, name, begin, end, visible, introduce=None, expires=None):
        self.type = type_
        self.name = name
        self.time_begin = begin
        self.time_end = end
        self.answer_visible = visible
        self.introduce = introduce
        if expires is None:
            expires = end-begin
        else:
            expires *= 60
        self.expires = expires

    def to_json_as_student(self, detail=False):
        user = g.current_user
        if hasattr(user, "user"):
            user = user.user

        key = "task_finished:"+str(self.id)
        if not r.sismember(key, user.id):
            finished = False
        else:
            finished = True
        data = {
            "self": request.host_url[0:-1] + url_for('course_bp.task', tid=self.id),
            "type": self.type,
            "id": self.id,
            "task_name": self.name,
            "time_begin": format_time(self.time_begin),
            "time_end": format_time(self.time_end),
            "finished": finished,
            "time_excess": not self.time_begin < time() < self.time_end,
            "answer_visible": self.answer_visible,
            "max_score": self.max_score,
            "create_at": format_time(self.create_at)
        }
        data_statistic = {
            "statistic_select": self.generate_prob_statistic("select"),
            "statistic_blank": self.generate_prob_statistic("blank"),
            "statistic_subjective": self.generate_prob_statistic("subjective"),
        }
        data["statistic"] = data_statistic
        show_answer = True if (finished and self.answer_visible) else False
        if detail:
            data_detail = {
                "problems": [prob.to_json(show_answer) for prob in self.problems]
            }

            if self.type == "exam":
                key = "exam_begin:tid:{}:uid:{}".format(self.id, user.id)
                exam_begin = r.get(key)
                exam_begin = float(exam_begin) if exam_begin is not None else None
                exam_status = {
                    'exam_started': 1 if exam_begin is not None else 0,
                    'exam_time_excess': time()-exam_begin > self.expires if exam_begin is not None else 0,
                    'exam_end': format_time(exam_begin + self.expires) if exam_begin is not None else None
                }
                data_detail.update(exam_status)

            data.update(data_detail)
        return data

    def to_json_as_teacher(self):
        data = {
            "self": request.host_url[0:-1] + url_for('course_bp.task', tid=self.id),
            "type": self.type,
            "id": self.id,
            "task_name": self.name,
            "time_begin": format_time(self.time_begin),
            "time_end": format_time(self.time_end),
            "time_excess": not self.time_begin < time() < self.time_end,
            "answer_visible": self.answer_visible,
            "max_score": self.max_score,
            "create_at": format_time(self.create_at)
        }
        return data

    def to_json_as_course(self, **options):
        if g.current_user.id == self.teacher.user.id:
            resp = self.to_json_as_teacher()
        else:
            resp = self.to_json_as_student(**options)
        return resp

    @classmethod
    def list_to_json(cls, tasks, type_, **options):
        bp_map = {"teacher": "teacher_bp", "student": "student_bp", "course": "course_bp"}
        schema_map = {"teacher": cls.to_json_as_teacher, "student": cls.to_json_as_student, "course": cls.to_json_as_course}
        bp_name = bp_map[type_]
        schema = schema_map[type_]
        data = {
            "count": len(tasks),
            "tasks": [schema(task, **options) for task in tasks]
        }
        return data

    def judge_max_score(self):
        max_score = 0
        probs = self.problems
        for prob in probs:
            max_score += int(prob.max_score)
        self.max_score = max_score
        return max_score

    def statistic(self, detail=False):
        answers = self.answers
        finished = [answer.student for answer in answers]
        unfinished = set(self.students).difference(set(finished))
        finish_rate = 1.0 * len(finished) / len(self.students) if len(self.students) is not 0 else 0
        pass_line = self.max_score * 0.6

        count_pass = 0
        score_sum = 0
        pass_detail = []
        fail_detail = []
        section_count = dict()
        for i in range(0, int(self.max_score/10)):
            section_count[i*10] = 0
        for answer in answers:
            if answer.score >= pass_line:
                count_pass += 1
                pass_detail.append(answer.student.user.name)
            else:
                fail_detail.append(answer.student.user.name)
            score_sum += answer.score
            section_count[int(answer.score/10)*10] += 1
        data = {
            "finish_rate": finish_rate,
            "pass_rate": 1.0 * count_pass / len(finished) if len(finished) is not 0 else 0,
            "average": 1.0 * score_sum / len(finished) if len(finished) is not 0 else 0,
            "finish_cnt": len(finished),
            "pass_cnt": count_pass,
            "total_cnt": len(self.students)
        }
        if detail:
            data_detail = {
                "finished_detail": [student.user.name for student in finished],
                "unfinished_detail": [student.user.name for student in unfinished],
                "pass_detail": pass_detail,
                "fail_detail": fail_detail,
                "section_count": section_count
            }
            data.update(data_detail)
        return data

    def generate_prob_statistic(self, prob_type):
        probs = self.problems
        if prob_type in current_app.config['SELECT_TYPE']:
            prob_type = 'select'
        statistic = dict()
        statistic['count'] = 0
        statistic['sum'] = 0
        for prob in probs:
            if prob.type == prob_type:
                statistic['count'] += 1
                statistic['sum'] += prob.max_score
        return statistic


class Problem(db.Model):
    id_name = "prob_id"

    id = db.Column(db.String(36), primary_key=True, index=True, default=uuid4)
    type = db.Column(db.Enum('select', 'blank', 'subjective', 'mselect', "judge"))
    order = db.Column(db.Integer, nullable=False)
    content = db.Column(db.Text)
    max_score = db.Column(db.Integer)
    media = db.Column(db.Text)  # include a list of url
    answer = db.Column(db.Text)  # if type is 'blank', it include a list of text
    answer_detail = db.Column(db.Text)  # include a dict has attr 'type'[text, url] and 'content'
    create_at = db.Column(db.Float, default=time)

    task_id = db.Column(db.Integer, db.ForeignKey("task.id"))
    task = db.relationship("Task", back_populates='problems')

    answers = db.relationship("Answer", back_populates='problem', cascade='all')

    def __init__(self, order, type_, content=None, medias=None, max_score=5, answer=None, answer_detail=None):
        """
        :param medias: a list containing medias' uuid
        :param answer: when type is "select", expected ['A' | 'B' | 'C' | 'D'].
                       when type is "blank", expected a list of answer
        :param answer_detail: expected a dict, dict example: {"type": ['media', 'text'], "content":"text or uuid"}
        """
        self.type = type_
        self.content = pickle.dumps(content)
        self.max_score = max_score
        self.order = order
        self.answer_detail = answer_detail
        if medias is not None:
            self.media = pickle.dumps(medias)
        if answer is not None:
            if isinstance(answer, str):
                answer = [answer]
            self.answer = pickle.dumps(answer)

    def to_json(self, return_answer=False):
        data = {
            "type": self.type,
            "order": self.order,
            "id": self.id,
            "content": pickle.loads(self.content),
            "medias": Media.load_medias_from_uuid_list(pickle.loads(self.media)) if self.media is not None else None,
            "max_score": self.max_score,
            "create_at": format_time(self.create_at),
            "picture_exist": 1 if self.media is not None else 0
        }
        if return_answer:
            data_answer = {
                "answer": pickle.loads(self.answer) if self.answer is not None else None,
                # "answer_detail": self.detail_answer_to_json()
                "answer_detail": self.answer_detail
            }
            print(data_answer)
            data.update(data_answer)
        return data

    def detail_answer_to_json(self):
        answer_detail = pickle.loads(self.answer_detail)
        if answer_detail['type'] is "media":
            media = Media.query.get(answer_detail['content'])
            answer_detail['content'] = media.to_json()
        return answer_detail

    def statistic(self, detail=False):
        answers = self.answers
        count_students = len(self.task.students)
        pass_line = self.max_score * 0.6
        score_sum = 0
        count_pass = 0
        count_correct = 0
        pass_detail = []
        fail_detail = []
        correct_detail = []

        for answer in answers:
            student = answer.student.user.name
            score_sum += answer.score
            if answer.score >= pass_line:
                count_pass += 1
                pass_detail.append(student)
                if answer.score == self.max_score:
                    count_correct += 1
                    correct_detail.append(student)
            else:
                fail_detail.append(student)

        data = {
            "pass_rate": count_pass / count_students if count_students is not 0 else 0,
            "correct_rate": count_correct / count_students if count_students is not 0 else 0,
            "average": score_sum / count_students if count_students is not 0 else 0
        }
        data_detail = {
            "pass_detail": pass_detail,
            "fail_detail": fail_detail,
            "correct_detail": correct_detail
        }
        if detail:
            data.update(data_detail)

        return data

    @staticmethod
    def create_prob(data):
        # expected a dict contain prob info
        order = data['order']
        prob_type = data['type']
        content = data['content']
        max_score = data['max_score']
        answer = data['answer']
        answer_detail = data['answer_detail']
        medias = request.files.getlist('problem' + str(order), None)
        media_uuid_list = Media.save_medias(medias, 'problem')
        new_prob = Problem(order, prob_type, content, media_uuid_list, max_score, answer, answer_detail)
        return new_prob


class TaskAnswer(db.Model):
    id_name = "task_answer_id"

    id = db.Column(db.String(36), primary_key=True, default=uuid4)
    status = db.Column(db.Boolean, server_default=db.text('0'))
    score = db.Column(db.Integer, server_default=db.text('0'))
    create_at = db.Column(db.Float, default=time)
    update_at = db.Column(db.Float, default=time, onupdate=time)

    answers = db.relationship("Answer", back_populates='task_answer', cascade='all')

    student_id = db.Column(db.Integer, db.ForeignKey('student.sid'))
    student = db.relationship("Student", back_populates='answers')

    task_id = db.Column(db.String(36), db.ForeignKey('task.id'))
    task = db.relationship("Task", back_populates='answers')

    def __init__(self):
        pass

    def to_json(self,detail=False):
        data = {
            "id": self.id,
            "status": self.status,
            "score": self.score,
            "create_at": format_time(self.create_at),
            "update_at": format_time(self.update_at)
        }
        if detail:
            if self.task.answer_visible:
                correct_ans = True
            else:
                correct_ans = False
            data_detail = {
                "answers": [answer.to_json(return_correct_answer=correct_ans) for answer in self.answers]
            }
            data.update(data_detail)
        return data

    def judge_score(self):
        score = 0
        answers = self.answers
        for answer in answers:
            score += answer.score
        self.score = score
        return score

    @staticmethod
    def delete(task_answer):
        for answer in task_answer.answers:
            if answer.media is not None:
                medias = Media.load_medias_from_uuid_list(pickle.loads(answer.media), return_model=True)
                for media in medias:
                    Media.delete(media)
        db.session.delete(task_answer)


class Answer(db.Model):
    id = db.Column(db.String(36), primary_key=True, default=uuid4)
    content = db.Column(db.Text)
    media = db.Column(db.Text)
    order = db.Column(db.Integer)
    score = db.Column(db.Integer)
    comment = db.Column(db.Text)
    create_at = db.Column(db.Float, default=time)
    update_at = db.Column(db.Float, default=time, onupdate=time)

    problem_id = db.Column(db.String(36), db.ForeignKey("problem.id"))
    problem = db.relationship("Problem", back_populates='answers')

    task_answer_id = db.Column(db.String(36), db.ForeignKey("task_answer.id"))
    task_answer = db.relationship("TaskAnswer", back_populates='answers')

    student_id = db.Column(db.Integer, db.ForeignKey("student.sid"))
    student = db.relationship("Student", back_populates='prob_answers')

    def __init__(self, order, content=None, medias=None):
        self.order = order
        if content is not None:
            if not isinstance(content, list):
                content = [content]
            self.content = pickle.dumps(content)
        if medias is not None:
            self.media = pickle.dumps(medias)
        self.score = 0

    def to_json(self, with_problem=False, return_correct_answer=False):
        data = {
            "id": str(self.id),
            "content": pickle.loads(self.content) if self.content is not None else None,
            "medias": Media.load_medias_from_uuid_list(pickle.loads(self.media)) if self.media is not None else None,
            "score": self.score,
            "order": self.order,
            "comment": self.comment,
            "answer_at": format_time(self.create_at),
            "update_at": format_time(self.update_at)
        }
        if with_problem:
            data_problem = self.problem.to_json(return_correct_answer)
            data_problem['student_answer'] = data
            data = data_problem
            return data
        if return_correct_answer:
            data_answer = {
                "correct_answer": pickle.loads(self.problem.answer) if self.problem.answer is not None else None,
                # "answer_detail": self.detail_answer_to_json()
                "answer_detail": self.problem.answer_detail
            }
            data.update(data_answer)
        return data

    def judge_score(self):
        if self.content is None:
            self.score = 0
            return 0

        prob = self.problem
        answers = pickle.loads(prob.answer) if prob.answer is not None else None
        my_ans = pickle.loads(self.content)
        max_score = prob.max_score
        if prob.type in ['select', 'mselect', 'judge']:
            answers = set(answers)
            my_ans = set(my_ans)
            if answers == my_ans:
                score = max_score
            else:
                score = 0
        elif prob.type is 'blank':
            score = max_score
            for i in range(0, len(answers)):
                if my_ans[i] != answers[i]:
                    score -= 1.0*max_score/len(answers)
        else:
            score = 0
        self.score = score
        return score

    @staticmethod
    def create_answer(answer, student, problem):
        content = answer.get('content')
        order = answer.get("order")
        medias = request.files.getlist('answer' + str(order))
        media_uuid_list = Media.save_medias(medias, 'answer') if len(medias) is not 0 else []
        new_answer = Answer(order, content, media_uuid_list)
        new_answer.student = student
        new_answer.problem = problem
        if new_answer.problem.type is not "subjective":
            new_answer.judge_score()
        return new_answer


class Media(db.Model):
    id_name = "media_id"

    id = db.Column(db.String(36), primary_key=True)
    name = db.Column(db.String(36))
    url = db.Column(db.Text, unique=False)
    type = db.Column(db.Enum('picture', 'audio', 'video', 'word', 'excel', 'ppt', 'pdf', 'python', 'cpp'))
    upload_at = db.Column(db.Float, default=time)

    def __init__(self, url, uuid=None, name=None):
        if uuid is None:
            uuid = uuid4()
        self.id = uuid
        if name is None:
            name = self.id
        self.name = name
        self.url = url
        self.type = guess_type(url)

    def to_json(self):
        data = {
            'uuid': str(self.id),
            "name": self.name,
            'type': self.type,
            'url': self.url,
            'upload_at': format_time(self.upload_at)
        }
        return data

    @staticmethod
    def save_medias(medias, media_type, return_model=False):
        media_list = []
        for media in medias:
            new_media = Media.save_media(media, media_type, return_model=return_model, commit=False)
            media_list.append(new_media)
        db.session.commit()
        return media_list

    @staticmethod
    def save_media(media, media_type, name=None, return_model=False, commit=True):
        filename = media.filename
        if filename[-1] is "\"":
            filename = filename[0:-1]
        postfix = filename.split('.')[-1]
        if postfix == 'blob':
            postfix = 'jpg'
        uuid = uuid4()
        if name is None:
            name = uuid
        sub_path = "/{}/{}.{}".format(media_type, uuid, postfix)
        save_path = os.path.abspath(current_app.static_folder + sub_path)
        try:
            media.save(save_path)
        except FileNotFoundError:
            os.makedirs(os.path.split(save_path)[0])
            media.save(save_path)
        url = request.host_url[0:-1] + current_app.static_url_path + sub_path
        new_media = Media(url, uuid, name)
        db.session.add(new_media)
        if commit:
            db.session.commit()
        if return_model:
            return new_media
        else:
            return new_media.id

    @staticmethod
    def load_medias_from_uuid_list(media, return_model=False):
        media_uuid_list = media
        media_list = []
        for uuid in media_uuid_list:
            media = Media.load_media_from_uuid(uuid, return_model)
            media_list.append(media)
        return media_list

    @staticmethod
    def load_media_from_uuid(uuid, return_model=False):
        media = Media.query.get(uuid)
        if return_model:
            return media
        return media.to_json()

    @staticmethod
    def delete(media):
        path = current_app.static_folder + media.url.replace(request.host_url[:-1] + current_app.static_url_path, "")
        try:
            os.remove(os.path.abspath(path))
        except FileNotFoundError:
            pass
        db.session.delete(media)

    @staticmethod
    def random_avatar(return_model=False):
        url = current_app.config["HOST_URL"] + current_app.static_url_path + \
              "/avatars/user/banner{}.jpg".format(random.choice([6, 7, 8, 13, 14]))
        new_avatar = Media(url)
        db.session.add(new_avatar)
        db.session.commit()
        if return_model:
            return new_avatar
        return new_avatar.id


class Discussion(db.Model):
    id_name = "discus_id"

    id = db.Column(db.String(36), primary_key=True, default=uuid4)
    content = db.Column(db.Text)
    creat_at = db.Column(db.Float, default=time)
    update_at = db.Column(db.Float, default=time, onupdate=time)

    course_id = db.Column(db.Integer, db.ForeignKey("course.id"))
    course = db.relationship("Course", back_populates='discussions')

    master_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    master = db.relationship("User", back_populates='discussions')

    comments = db.relationship("Comment", back_populates='discussion', cascade="all")

    def __init__(self, content):
        self.content = content

    def to_json(self, detail=False):
        data = {
            "id": self.id,
            "content": self.content,
            "collections": r.scard("collect_discussion:{}".format(str(self.id))),
            "collected": g.current_user.collected(str(self.id), "discussion"),
            "post_at": format_time(self.creat_at),
            "update_at": format_time(self.update_at),
            "user": self.master.to_json()
        }
        if detail:
            data_detail = {
                "comments_count": len(self.comments)
            }
            data_detail.update(Comment.list_to_json(self.comments))
            data.update(data_detail)
        return data

    @staticmethod
    def list_to_json(discussions):
        data = {
            "count": len(discussions),
            "discussions": [discussion.to_json() for discussion in discussions]
        }
        return data


class Comment(db.Model):
    id_name = "comment_id"

    id = db.Column(db.String(36), primary_key=True, default=uuid4)
    content = db.Column(db.Text)
    replies = db.Column(db.Text)
    reply = db.Column(db.String(36))
    creat_at = db.Column(db.Float, default=time)

    discussion_id = db.Column(db.String(36), db.ForeignKey("discussion.id"))
    discussion = db.relationship("Discussion", back_populates='comments')

    author_id = db.Column(db.Integer, db.ForeignKey("user.id"))
    author = db.relationship("User", back_populates="comments")

    def __init__(self, content, reply=None):
        self.content = content
        self.reply = reply
        self.replies = pickle.dumps([])
        self.id = uuid4()

    def to_json(self):
        replies = []
        for reply_id in pickle.loads(self.replies):
            reply = Comment.query.filter_by(id=reply_id).first()
            if reply is not None:
                replies.append(reply.to_json())
        data = {
            "id": str(self.id),
            "content": self.content,
            "likes": r.scard("like_comment:{}".format(str(self.id))),
            "liked": g.current_user.liked(str(self.id), "comment"),
            "replies": replies,
            "reply": self.reply,
            "post_at": format_time(self.creat_at),
            "author": self.author.to_json()
        }
        return data

    @staticmethod
    def list_to_json(comments):
        comment_list = []
        count = len(comments)
        for comment in comments:
            if comment.reply is None:
                comment_list.append(comment.to_json())
                count -= 1
        data = {
            "count": count,
            "comments": comment_list
        }
        return data

    @staticmethod
    def page_to_json(pagination, discus_id):
        page = pagination.page
        per_page = pagination.per_page
        max_page = pagination.pages
        comments = pagination.items
        has_next = pagination.has_next
        has_prev = pagination.has_prev
        data = Comment.list_to_json(comments)
        data['max_page'] = max_page
        data['has_next'] = has_next
        data['has_prev'] = has_prev
        if has_next:
            data['next_page'] = request.host_url[0:-1] + url_for("course_bp.comments", per_page=per_page, page=page + 1, discus_id=discus_id)
        else:
            data['next_page'] = None
        if has_prev:
            data['prev_page'] = request.host_url[0:-1] + url_for("course_bp.comments", per_page=per_page, page=page - 1, discus_id=discus_id)
        else:
            data['prev_page'] = None
        return data

    @property
    def course(self):
        return self.discussion.course


class Notice(db.Model):
    id_name = "notice_id"

    id = db.Column(db.String(36), primary_key=True, index=True, default=uuid4)
    title = db.Column(db.String, nullable=False)
    content = db.Column(db.Text, nullable=False)
    create_at = db.Column(db.Float, default=time())

    course_id = db.Column(db.Integer, db.ForeignKey("course.id"))
    course = db.relationship("Course", back_populates='notices')

    def __init__(self, title, content):
        self.content = content
        self.title = title

    def to_json(self, detail=False):

        read = 0
        key = "notice:read:{}".format(self.id)
        if r.sismember(key, g.current_user.id):
            read = 1

        data = {
            "id": self.id,
            "self": request.host_url[:-1] + url_for("course_bp.notice", notice_id=self.id, cid=self.course.id),
            "title": self.title,
            "read": read
        }
        if detail:
            data_detail = {
                "content": self.content,
                "create_at": format_time(self.create_at)
            }
            data.update(data_detail)
        return data

    @staticmethod
    def list_to_json(notices):
        data = {
            "count": len(notices),
            "notices": [notice.to_json(detail=True) for notice in notices]
        }
        return data


class Commit:

    def __init__(self, course, expires):
        self.id = uuid4()
        self.begin = time()
        self.end = self.begin + expires
        self.finished = list()
        self.unfinished = list()
        for student in course.students:
            self.unfinished.append(student.user.name)

        r.lpush("commits:" + str(course.id), pickle.dumps(self))

    def __getitem__(self, item):
        if hasattr(self, item):
            return getattr(self, item)
        raise KeyError(item)

    @staticmethod
    def get_current_commit(course):
        # get a current effective commit
        current_commit = r.lindex("commits:{}".format(course.id), 0)
        if current_commit is not None:
            current_commit = pickle.loads(current_commit)

        time_now = time()
        if current_commit is not None and (current_commit.begin < time_now < current_commit.end):
            return current_commit
        else:
            return None

    @staticmethod
    def get_commits(course):
        key = "commits:{}".format(course.id)
        zip_commits = r.lrange(key, 0, r.llen(key))

        commits = list()
        for zip_commit in zip_commits:
            commits.append(pickle.loads(zip_commit))

        return commits

    def make_commit(self, student):
        self.finished.append(student.name)
        if student.name in self.unfinished:
            self.unfinished.remove(student.name)

    def statistic(self):
        return {
            "finished": self.finished,
            "unfinished": self.unfinished,
            "count_finished": len(self.finished),
            "count_unfinished": len(self.unfinished),
            "finish_rate": len(self.finished) / (len(self.finished) + len(self.unfinished))
            if len(self.finished) is not 0 else 0
        }

    def json(self):
        return {
            "id": self.id,
            "finished": self.finished,
            "unfinished": self.unfinished,
            "begin": self.begin,
            "end": self.end
        }

    @staticmethod
    def validate_commit_time(course_id, expires):
        begin = time()
        end = begin + expires
        if begin > end:
            return False, "invalid time"

        old_commit = r.lindex("commits:" + str(course_id), 0)
        if old_commit is None:
            return True, "OK"

        old_commit = pickle.loads(old_commit)
        if old_commit['end'] > begin:
            return False, "already exist a commit now"

        return True, "OK"

    @staticmethod
    def list_to_json(commits, statistic=False):
        data = {
            "count": len(commits)
        }
        if statistic:
            data["items"] = [commit.statistic() for commit in commits]
        else:
            data['items'] = [commit.json() for commit in commits]
        return data


def page_to_json(class_type, items, **options):
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 20))

    length = len(items)
    items = items[(page - 1) * per_page:page * per_page]

    data = class_type.list_to_json(items, **options)

    data_pagination = {
        "max_page": ceil(length/per_page),
        "have_next": 1 if length > page * per_page else 0,
        "have_prev": 1 if page != 1 else 0,
        "next_page": request.base_url + "?page={}&per_page={}".format(page+1, per_page),
        "prev_page": request.base_url + "?page={}&per_page={}".format(page-1, per_page)
    }
    data.update(data_pagination)

    return data
