import redis
from time import time
from flask import g, request
from flask_restful import Resource

from app.modules import Problem, Task, page_to_json, TaskAnswer, Answer, Media
from app.interceptors import role_required, resource_found_required
from app.helpers import make_resp, api_abort
from app.extensions import pool, db

from ..reqparsers import task_create_reqparser, answer_submit_reqparser, check_answer_reqparser


r = redis.Redis(connection_pool=pool)


class TaskListAPI(Resource):
    # url: /<int:cid>/tasks?type="exam"/"test"

    method_decorators = {"get": [role_required("student"), resource_found_required('course')],
                         "post": [role_required("teacher"), resource_found_required('course')]}

    def get(self, cid):
        # get tasks according to task type
        task_query = Task.query.filter_by(course_id=cid)
        task_type = request.args.get("type")
        if task_type is not None:
            task_query = task_query.filter_by(type=task_type)
        tasks = task_query.all()

        resp = page_to_json(Task, tasks, type_="course", detail=False)
        return make_resp(resp)

    def post(self, cid):
        # initialize a new task
        course = g.current_course
        data = task_create_reqparser.parse_args()
        new_task = Task(data['type'], data['name'], data['t_begin'], data['t_end'],
                        int(data['ans_visible']), data['introduce'], data['expires'])

        # create problems
        problems = eval(data['problems'])
        for prob in problems.values():
            new_prob = Problem.create_prob(prob)
            new_task.problems.append(new_prob)

        # attach new task to students' tasks
        new_task.judge_max_score()
        for student in course.students:
            new_task.students.append(student)

        # commit change to db
        course.tasks.append(new_task)
        new_task.teacher = course.teacher
        db.session.commit()

        resp = new_task.to_json_as_student(detail=True)
        return make_resp(resp)


class TaskAPI(Resource):
    # url: /task/<int:tid>
    # if finished, will return the correct answer
    method_decorators = {"get": [role_required("student", "task"), resource_found_required('task')],
                         "delete": [role_required("teacher", "task"), resource_found_required('task')]}

    def get(self, tid):
        set_exam_expires(g.current_user, g.current_task)
        resp = g.current_task.to_json_as_course(detail=True)
        return make_resp(resp)

    def delete(self, tid):
        db.session.delete(g.current_task)
        db.session.commit()
        return make_resp("OK")


class AnswerSubmitAPI(Resource):
    # url: /task/<string:tid>/submit
    method_decorators = [role_required("student", "task"), resource_found_required('task')]

    def post(self, tid):
        user = g.current_user
        task = g.current_task
        time_now = time()
        if not task.time_begin <= time_now <= task.time_end:
            return api_abort(403, "not in the time")

        # delete existed answer
        exist_task_answer = set(task.answers).intersection(set(user.student.answers))
        if exist_task_answer:
            exist_task_answer = exist_task_answer.pop()
            TaskAnswer.delete(exist_task_answer)

        new_task_answer = TaskAnswer()

        # get task problems
        problems = dict()
        for prob in task.problems:
            problems[prob.order] = prob

        # get answers
        answers = answer_submit_reqparser.parse_args()['answers']
        if not isinstance(answers, list):
            answers = eval(answers)

        # create answers
        for answer in answers:
            if not isinstance(answer, dict):
                answer = eval(answer)
            new_answer = Answer.create_answer(answer, user.student, problems[answer['order']])
            new_task_answer.answers.append(new_answer)

        # build relationship
        new_task_answer.student = user.student
        new_task_answer.task = task

        # commit changes to db
        new_task_answer.judge_score()
        r.sadd("task_finished:"+task.id, user.id)
        db.session.add(new_task_answer)
        db.session.commit()

        resp = new_task_answer.to_json(detail=True)
        return make_resp(resp)


class TaskAnswerAPI(Resource):
    # url: /task/<string:tid>/my_answer
    method_decorators = [role_required("student", "task"), resource_found_required('task')]

    def get(self, tid):
        task = g.current_task
        user = g.current_user
        task_answer = set(user.student.answers).intersection(set(task.answers))
        if not task_answer:
            return api_abort(4044, "have not finished the task")
        task_answer = task_answer.pop()
        resp = task_answer.to_json(detail=True)
        return make_resp(resp)


class CheckAnswerAPI(Resource):
    # url: /task/<string:tid>/check_answer
    method_decorators = [role_required("teacher", "task"), resource_found_required('task')]

    def get(self, tid):
        task_answer = TaskAnswer.query.filter_by(task_id=tid, status=0).first()
        if task_answer is None:
            return api_abort(4045, "all answers have been checked")
        resp = task_answer.to_json(detail=True)
        return make_resp(resp)

    def post(self, tid):
        check_res_list = check_answer_reqparser.parse_args()['check_res']
        task_answer_id = check_answer_reqparser.parse_args()['task_answer_id']
        check_res_list = eval(check_res_list)

        task_answer = TaskAnswer.query.get(task_answer_id)

        answers = dict()
        answer = task_answer.answers
        for ans in answer:
            answers[int(ans.order)] = ans

        for check_res in check_res_list:
            order = check_res['order']
            ans = answers[order]

            score = check_res['score'] if check_res['score'] is not None else ans.score
            if score > ans.problem.max_score:
                return api_abort(400, "the score of answer ordered {} is too high".format(order))

            ans.score = score
            ans.comment = check_res.get("comment", None)

        task_answer.judge_score()
        db.session.commit()
        return make_resp("OK")


class TaskStatisticAPI(Resource):
    # url: /task/<string:tid>/statistic?detail=True
    method_decorators = [role_required("teacher", "task"), resource_found_required("task")]

    def get(self, tid):
        detail = request.args.get("detail", False)
        data = g.current_task.statistic(detail)
        return make_resp(data)


class ProbStatisticAPI(Resource):
    # url: /task/<string:tid>/statistic/problems?order=<int:order>&detail=True
    method_decorators = [role_required("teacher", "task"), resource_found_required("task")]

    def get(self, tid):
        order = request.args.get("order", None)
        if order is None:
            return api_abort(400, "param order is needed")
        order = int(order)

        problem = None
        for prob in g.current_task.problems:
            if prob.order == order:
                problem = prob
                break
        if problem is None:
            return api_abort(400, "problem order {} is not found".format(order))

        detail = request.args.get("detail", False)
        data = problem.statistic(detail)
        return make_resp(data)


def set_exam_expires(user, task):
    key = "exam_begin:tid:{}:uid:{}".format(task.id, user.id)
    if r.get(key) is None:
        r.set(key, time())


def register_recourse_task(api):
    api.add_resource(TaskListAPI, "/<int:cid>/tasks", endpoint="tasks")
    api.add_resource(TaskAPI, "/task/<string:tid>", endpoint="task")
    api.add_resource(AnswerSubmitAPI, "/task/<string:tid>/submit")
    api.add_resource(TaskAnswerAPI, "/task/<string:tid>/my_answer")
    api.add_resource(CheckAnswerAPI, "/task/<string:tid>/check_answer")
    api.add_resource(TaskStatisticAPI, "/task/<string:tid>/statistic")
    api.add_resource(ProbStatisticAPI, "/task/<string:tid>/statistic/problems")
