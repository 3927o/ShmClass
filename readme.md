关于token：在一些请求中要在请求头的Authorization带上token信息。token分为两种，access token与refresh token, access token 的过期时间为七天，refresh token的过期时间为一个月，若access token 已过期我会根据refresh token发送生成新的token并伴随原请求一起返回，返回示例

```
{
	"status": 200,
	"message": "succeed",
	"data": {原请求应返回的数据},
	"access_token": access_token,
    "refresh_token": refresh_token,
    "expires_access": 3600*24*7,
    "expires_refresh": 3600*24*30
}
```

token方面我搞了一个便于测试的东西，当你Authorization的值为 ” uid;uid “ 时，你将会以uid对应的用户登录

#### tips

1.统一在请求url前面加一个/api,比如原请求url为 /user/current 实际请求URL为 /api/user/current

2.因为手机短信限制太多，所以所有有关短信的我都变成邮件了

3.返回的时间都是时间戳，要改成某一格式的时间的话跟我说

4.所有返回一列表数据的接口都支持通过“page"以及"per_page"的查询参数进行分页，默认page=1,per_page=20

[TOC]



## 有关认证与账户

### 用户注册

#### 1.发送验证码：

##### 请求方式

请求方法：POST

请求URL：http://shmclass.mr-lin.site/auth/verify_code

请求参数：

| 请求参数 | 必须 | 类型   | 说明                                                         |
| -------- | ---- | ------ | ------------------------------------------------------------ |
| type     | 是   | int    | ['signup', 'login', 'changeMail', 'ChangePassword', 'DelAccount'] |
| email    | 是   | string |                                                              |

上面的type，比如用户是要发送修改密码的验证码，因为changePassword对应的下标为3，所以type应该为3

##### 返回示例

data: "OK"



#### 2.验证电话号码是否已注册

##### 请求方式

请求方法：GET

请求URL：/auth/check/email?email={{email}}

请求参数：无

##### 返回示例

```
{
	"status": 1  # or 0
}
```



#### 3.验证用户名是否已注册

##### 请求方式

请求方法：GET

请求URL：/auth/check/nickname?nickname={{name}}

请求参数：无

##### 放回示例

```bash
{
	"status": 1  # or 0
}
```



#### 4.发送注册信息

##### 请求方式

请求方法：POST

请求URL：/auth/signup

请求参数：

| 请求参数 | 必须 | 类型 | 说明 |
| -------- | ---- | ---- | ---- |
| nickname | 1    | str  |      |
| email    | 1    | str  |      |
| password | 1    | str  |      |
| code     | 1    | str  |      |

##### 返回示例

```bash
{
    "data": {
        "access_token": "access_token",
        "avatar": "http://127.0.0.1:5000/static/avatars/user/banner13.jpg",
        "expires_access": 604800,
        "expires_refresh": 2592000,
        "gender": "secret",
        "introduce": null,
        "nickname": "linwei",
        "refresh_token": "refresh_token",
        "school": null,
        "self": "http://127.0.0.1:5000/api/student/3/info",
        "uid": 3
    },
    "message": "succeed",
    "status": 2000
}
```



### 用户登录

#### 1.用户名密码登录

##### 请求方式

请求方式：POST

请求URL：/auth/login?method=0

请求参数：

| 请求参数 | 必须 | 类型 | 说明 |
| -------- | ---- | ---- | ---- |
| username | 1    | str  |      |
| password | 1    | str  |      |

#### 2.验证码登录

##### 请求方式

请求方式：POST

请求URL：/auth/login?method=1

请求参数：

| 请求参数 | 必须 | 类型 | 说明 |
| -------- | ---- | ---- | ---- |
| mail     | 1    | str  |      |
| code     | 1    | str  |      |

##### 返回示例

```bash
{
    "data": {
        "access_token": "access_token",
        "avatar": "http://127.0.0.1:5000/static/avatars/user/banner6.jpg",
        "expires_access": 604800,
        "expires_refresh": 2592000,
        "gender": "secret",
        "introduce": null,
        "nickname": "lin",
        "refresh_token": "refresh_token",
        "school": null,
        "self": "http://127.0.0.1:5000/api/student/2/info",
        "uid": 2
    },
    "message": "succeed",
    "status": 2000
}
```



### 改密码

##### 请求方式

请求方法：POST

请求URL：/auth/account/pwd/reset

请求参数：

| 请求参数    | 必须 | 类型 | 说明 |
| ----------- | ---- | ---- | ---- |
| verify_code | 1    | str  |      |
| new_pwd     | 1    | str  |      |



##### 返回示例

```bash
"data" : "OK"
```

说明：无需token



### 改邮箱  

##### 请求方式

请求方法：POST

请求URL：/auth/account/email/reset

请求参数：

| 请求参数       | 必须 | 类型 | 说明 |
| -------------- | ---- | ---- | ---- |
| old_email_code | 1    | str  |      |
| new_email_code | 1    | str  |      |
| new_email      | 1    | str  |      |

##### 返回示例

```bash
"data" : "OK"
```

### 删除用户

##### 请求方式

请求方法：DELETE

请求URL：/auth/account/del

请求参数：

| 请求参数    | 必须 | 类型 | 说明 |
| ----------- | ---- | ---- | ---- |
| verify_code | 1    | str  |      |

##### 返回示例：

无



## 有关用户

### 教师

#### 教师信息

##### 请求方式

请求方法：GET

请求URL：/teacher/<int:uid>/info

请求参数：无

##### 返回示例

```bash
{
    "data": {
        "avatar": "http://127.0.0.1:5000/static/avatars/user/banner14.jpg",
        "gender": "secret",
        "introduce": null,
        "name": "3927",
        "school": null,
        "self": "http://127.0.0.1:5000/api/teacher/1/info",
        "uid": 1
    },
    "message": "succeed",
    "status": 2000
}
```

#### 当前教师信息

##### 请求方式

请求方法：GET

请求URL：/teacher/info

请求参数：无

##### 返回示例

```bash
{
    "data": {
        "avatar": "http://127.0.0.1:5000/static/avatars/user/banner14.jpg",
        "email": "1624497311@qq.com",
        "gender": "secret",
        "introduce": null,
        "name": "3927",
        "school": null,
        "self": "http://127.0.0.1:5000/api/teacher/1/info",
        "teacher_id": null,
        "telephone": null,
        "uid": 1
    },
    "message": "succeed",
    "status": 2000
}
```

#### 教师课程列表

##### 请求方式

请求方法：GET

请求URL：/teacher/info/courses

请求参数：无

##### 返回示例

```bash
{
    "data": {
        "count": 2,
        "courses": [
            {
                "avatar": null,
                "end_at": "2052/05/01 22:12:17",
                "id": 1,
                "introduce": "welcome",
                "name": "first class",
                "public": true,
                "self": "http://127.0.0.1:5000/api/course/1",
                "start_at": "1970/01/01 08:00:00",
                "time_excess": false
            }
        ],
        "have_next": 0,
        "have_prev": 0,
        "max_page": 1,
        "next_page": "http://127.0.0.1:5000/api/teacher/info/courses?page=2&per_page=20",
        "prev_page": "http://127.0.0.1:5000/api/teacher/info/courses?page=0&per_page=20",
        "self": "http://127.0.0.1:5000/api/teacher/info/courses"
    },
    "message": "succeed",
    "status": 2000
}
```

#### 教师作业列表

##### 请求方式

请求方法：GET

请求URL：/teacher/info/tasks

请求参数：无

##### 返回示例

```bash
{
    "data": {
        "count": 0,
        "have_next": 0,
        "have_prev": 0,
        "max_page": 0,
        "next_page": "http://127.0.0.1:5000/api/teacher/info/tasks?page=2&per_page=20",
        "prev_page": "http://127.0.0.1:5000/api/teacher/info/tasks?page=0&per_page=20",
        "tasks": []
    },
    "message": "succeed",
    "status": 2000
}
```

#### 教师认证状态

##### 请求方式

请求方法：GET

请求URL：/teacher/certificate/status

请求参数：无

##### 返回示例

```bash
{
    "data": 1,
    "message": "succeed",
    "status": 2000
}
```

#### 教师认证

##### 请求方式

请求方法：POST

请求URL：/teacher/certificate

请求参数：

| 请求参数         | 必须 | 类型 | 说明                             |
| ---------------- | ---- | ---- | -------------------------------- |
| school           | 1    | str  |                                  |
| role_id          | 1    | str  | 导入教师认证信息时表格中的教师id |
| certificate_code | 1    | str  |                                  |



##### 返回示例

```bash
{
    "data": "OK",
    "message": "succeed",
    "status": 2000
}
```

### 学生

#### 学生信息

##### 请求方式

请求方法：GET

请求URL：/student/<int:uid>/info

请求参数：无

##### 返回示例

```bash
{
    "data": {
        "avatar": "http://127.0.0.1:5000/static/avatars/user/banner14.jpg",
        "gender": "secret",
        "introduce": null,
        "nickname": "3927",
        "school": "福州大学",
        "self": "http://127.0.0.1:5000/api/student/1/info",
        "uid": 1
    },
    "message": "succeed",
    "status": 2000
}
```

#### 当前学生信息

##### 请求方式

请求方法：GET

请求URL：/student/info

请求参数：无

##### 返回示例

```bash
{
    "data": {
        "avatar": "http://127.0.0.1:5000/static/avatars/user/banner14.jpg",
        "class": null,
        "email": "1624497311@qq.com",
        "gender": "secret",
        "grade": null,
        "introduce": null,
        "name": "林炜",
        "nickname": "3927",
        "school": "福州大学",
        "self": "http://127.0.0.1:5000/api/student/1/info",
        "student_id": null,
        "telephone": null,
        "uid": 1
    },
    "message": "succeed",
    "status": 2000
}
```

#### 学生课程列表

##### 请求方式

请求方法：GET

请求URL：/student/info/courses

请求参数：无

##### 返回示例

```bash
{
    "data": {
        "count": 0,
        "courses": [],
        "have_next": 0,
        "have_prev": 0,
        "max_page": 0,
        "next_page": "http://127.0.0.1:5000/api/student/info/course?page=2&per_page=20",
        "prev_page": "http://127.0.0.1:5000/api/student/info/course?page=0&per_page=20",
        "self": "http://127.0.0.1:5000/api/student/info/course"
    },
    "message": "succeed",
    "status": 2000
}
```

#### 学生作业列表

##### 请求方式

请求方法：GET

请求URL：/student/info/tasks

请求参数：无

##### 返回示例

```bash
{
    "data": {
        "count": 0,
        "have_next": 0,
        "have_prev": 0,
        "max_page": 0,
        "next_page": "http://127.0.0.1:5000/api/student/info/tasks?page=2&per_page=20",
        "prev_page": "http://127.0.0.1:5000/api/student/info/tasks?page=0&per_page=20",
        "tasks": []
    },
    "message": "succeed",
    "status": 2000
}
```



#### 学生认证

##### 请求方式

请求方法：POST

请求URL：/studednt/certificate

请求参数：

| 请求参数         | 必须 | 类型 | 说明                             |
| ---------------- | ---- | ---- | -------------------------------- |
| school           | 1    | str  |                                  |
| role_id          | 1    | str  | 导入学生认证信息时表格中的学生id |
| certificate_code | 1    | str  |                                  |



##### 返回示例

```bash
{
    "data": "OK",
    "message": "succeed",
    "status": 2000
}
```



### 管理员

#### 导入学生认证信息

##### 请求方式

请求方法：POST
请求URL：/admin/import/student

请求参数：

| 请求参数 | 必须 | 类型 | 说明               |
| -------- | ---- | ---- | ------------------ |
| students | 1    | file |                    |
| school   | 1    | str  | 导入某一学校的学生 |



##### 返回示例

```bash
{
    "data": [
        {
            "certificate_code": "123456",
            "class_": "计3",
            "grade": "2019级",
            "name": "林炜",
            "school": "福州大学",
            "student_id": "031902321"
        },
        {
            "certificate_code": "123456",
            "class_": "软1",
            "grade": "2018级",
            "name": "林沧海",
            "school": "福州大学",
            "student_id": "031801111"
        },
        {
            "certificate_code": "123456",
            "class_": "计3",
            "grade": "2019级",
            "name": "张乐芃",
            "school": "fzu",
            "student_id": "031902341"
        }
    ],
    "message": "succeed",
    "status": 2000
}
```



#### 导入教师认证信息

##### 请求方式

请求方法：POST
请求URL：/admin/import/teacher

请求参数：

| 请求参数 | 必须 | 类型 | 说明               |
| -------- | ---- | ---- | ------------------ |
| teachers | 1    | file |                    |
| school   | 1    | str  | 导入某一学校的教师 |

##### 返回示例

```bash
{
    "data": [
        {
            "certificate_code": "123456",
            "name": "林炜",
            "school": "福州大学",
            "teacher_id": "031902321"
        },
        {
            "certificate_code": "123456",
            "name": "林沧海",
            "school": "福州大学",
            "teacher_id": "031801111"
        },
        {
            "certificate_code": "123456",
            "name": "张乐芃",
            "school": "fzu",
            "teacher_id": "031902341"
        }
    ],
    "message": "succeed",
    "status": 2000
}
```



#### 导入课程学生信息

##### 请求方式

请求方法：POST
请求URL：/admin/import/student/<int:course_id>

请求参数：

| 请求参数 | 必须 | 类型 | 说明 |
| -------- | ---- | ---- | ---- |
| excel    | 1    | file |      |

##### 返回示例

```bash
{
    "data": [
        "031902321",
        "031801111",
        "031902341"
    ],
    "message": "succeed",
    "status": 2000
}
```

说明：data为导入的学生学号列表



## 有关课程

### 课程信息及操作

#### 获取课程信息

##### 请求方式

请求方法：GET

请求URL：/course/<int:course_id>

请求参数：无

##### 返回示例

```bash
{
    "data": {
        "avatar": null,
        "create_status": 0,
        "end_at": "2052/05/01 22:12:17",
        "id": 1,
        "introduce": "welcome",
        "join_status": 0,
        "name": "first class",
        "public": true,
        "self": "http://127.0.0.1:5000/api/course/1",
        "start_at": "1970/01/01 08:00:00",
        "teacher": {
            "avatar": "http://127.0.0.1:5000/static/avatars/user/banner13.jpg",
            "gender": "secret",
            "introduce": null,
            "name": "3927",
            "school": null,
            "self": "http://127.0.0.1:5000/api/teacher/1/info",
            "uid": 1
        },
        "teacher_name": "3927",
        "time_excess": false
    },
    "message": "succeed",
    "status": 2000
}
```



#### 获取课程列表

##### 请求方式

请求方法：GET

请求URL：/course/course_list

请求参数：

##### 返回示例

```bash
{
    "data": {
        "count": 2,
        "courses": [
            {
                "avatar": null,
                "create_status": 1,
                "end_at": "2052/05/01 22:12:17",
                "id": 1,
                "introduce": "welcome",
                "join_status": 0,
                "name": "first class",
                "public": true,
                "self": "http://127.0.0.1:5000/api/course/1",
                "start_at": "1970/01/01 08:00:00",
                "teacher_name": "3927",
                "time_excess": false
            },
            {
                "avatar": null,
                "create_status": 1,
                "end_at": "2052/05/01 22:12:17",
                "id": 2,
                "introduce": null,
                "join_status": 0,
                "name": "deleted course",
                "public": true,
                "self": "http://127.0.0.1:5000/api/course/2",
                "start_at": "1970/01/01 08:00:00",
                "teacher_name": "3927",
                "time_excess": false
            }
        ],
        "have_next": 0,
        "have_prev": 0,
        "max_page": 1,
        "next_page": "http://127.0.0.1:5000/api/course/course_list?page=2&per_page=20",
        "prev_page": "http://127.0.0.1:5000/api/course/course_list?page=0&per_page=20",
        "self": "http://127.0.0.1:5000/api/course/course_list"
    },
    "message": "succeed",
    "status": 2000
}
```



#### 获取课程学生信息

##### 请求方式

请求方法：GET

请求URL：/course/<int:course_id>/students

请求参数：无

##### 返回示例

```bash
{
    "data": {
        "count": 0,
        "have_next": 0,
        "have_prev": 0,
        "items": [],
        "max_page": 0,
        "next_page": "http://127.0.0.1:5000/api/course/1/students?page=2&per_page=20",
        "prev_page": "http://127.0.0.1:5000/api/course/1/students?page=0&per_page=20"
    },
    "message": "succeed",
    "status": 2000
}
```

#### 创建课程

##### 请求方式

请求方法：POST

请求URL：/courses/course_list

请求参数：

| 请求参数  | 必须 | 类型        | 说明 |
| --------- | ---- | ----------- | ---- |
| name      | 1    | str         |      |
| public    | 1    | str         |      |
| introduce | 0    | str         |      |
| start_at  | 1    | float       |      |
| end_at    | 1    | float       |      |
| avatar    | 1    | file/binary |      |

##### 返回示例

```bash
{
    "data": {
        "avatar": "http://127.0.0.1:5000/static/avatars/course/1adb3c1f-a461-42fd-881d-7f8ce37aa840.jpg",
        "end_at": "2052/05/07 00:04:36",
        "id": 3,
        "introduce": "welcome",
        "name": "first class",
        "public": true,
        "self": "http://127.0.0.1:5000/api/course/3",
        "start_at": "1970/01/01 08:00:00",
        "time_excess": false
    },
    "message": "succeed",
    "status": 2000
}
```

#### 加入课程

只能通过该方式加入公开课

##### 请求方式

请求方法：POST

请求URL：/course/<int:course_id>/join

请求参数：无

##### 返回示例

```bash
{
    "data": "OK",
    "message": "succeed",
    "status": 2000
}
```

#### 退出课程

只能通过该方式加入公开课

##### 请求方式

请求方法：POST

请求URL：/course/<int:course_id>/join

请求参数：无

##### 返回示例

```bash
{
    "data": "OK",
    "message": "succeed",
    "status": 2000
}
```

#### 首页推荐课程

##### 请求方式

请求方法:GET

请求URL:/course/recommend?count_items=<int>

请求参数:无

##### 返回示例

默认返回五个课程

```bash
{
    "data": {
        "count": 3,
        "courses": [
            {
                "avatar": null,
                "create_status": 0,
                "end_at": "2052/05/01 22:12:17",
                "id": 1,
                "introduce": "welcome",
                "join_status": 0,
                "name": "first class",
                "public": true,
                "self": "http://127.0.0.1:5000/api/course/1",
                "start_at": "1970/01/01 08:00:00",
                "teacher_name": "3927",
                "time_excess": false
            },
            {
                "avatar": null,
                "create_status": 0,
                "end_at": "2052/05/01 22:12:17",
                "id": 2,
                "introduce": null,
                "join_status": 0,
                "name": "deleted course",
                "public": true,
                "self": "http://127.0.0.1:5000/api/course/2",
                "start_at": "1970/01/01 08:00:00",
                "teacher_name": "3927",
                "time_excess": false
            },
            {
                "avatar": "http://127.0.0.1:5000/static/avatars/course/1adb3c1f-a461-42fd-881d-7f8ce37aa840.jpg",
                "create_status": 0,
                "end_at": "2052/05/07 00:04:36",
                "id": 3,
                "introduce": "welcome",
                "join_status": 0,
                "name": "first class",
                "public": true,
                "self": "http://127.0.0.1:5000/api/course/3",
                "start_at": "1970/01/01 08:00:00",
                "teacher_name": "3927",
                "time_excess": false
            }
        ],
        "self": "http://127.0.0.1:5000/api/course/course_list"
    },
    "message": "succeed",
    "status": 2000
}
```



#### 删除课程

##### 请求方式

请求方法：DELETE

请求URL：/course/<int:cid>

请求参数：无

##### 返回示例

```bash
{
    "data": "OK",
    "message": "succeed",
    "status": 2000
}
```



#### 修改课程信息

##### 请求方式

请求方法：POST

请求URL：/course/<int:course_id>

请求参数：

| 请求参数  | 必须 | 类型  | 说明 |
| --------- | ---- | ----- | ---- |
| introduce | 0    | str   |      |
| start_at  | 0    | float |      |
| end_at    | 0    | float |      |

##### 返回示例

```bash
{
    "data": {
        "avatar": null,
        "end_at": "1970/04/27 01:46:40",
        "id": 1,
        "introduce": "get out!",
        "name": "first class",
        "public": true,
        "self": "http://127.0.0.1:5000/api/course/1",
        "start_at": "1970/01/01 08:00:01",
        "time_excess": true
    },
    "message": "succeed",
    "status": 2000
}
```

### 课程文件

#### 上传课程文件

##### 请求方式

请求方法：POST

请求URL：/course/<int:course_id>/medias/upload

请求参数：

| 请求参数   | 必须 | 类型 | 说明           |
| ---------- | ---- | ---- | -------------- |
| media      | 是   | file |                |
| chapter_id | 是   | int  |                |
| media_type | 是   | str  | document/movie |
| name       | 1    | str  |                |

若上传课程视频则media_type为movie,上传课程课件则media_type为document

##### 返回示例

```bash
{
    "data": {
        "name": "my picture",
        "type": "picture",
        "upload_at": "2020/08/28 10:43:46",
        "url": "http://127.0.0.1:5000/static/course/1/document/934c91d0-ff37-49d9-b2a0-e2169e157e6a.jpg",
        "uuid": "934c91d0-ff37-49d9-b2a0-e2169e157e6a"
    },
    "message": "succeed",
    "status": 2000
}
```



#### 获取课程文件列表

##### 请求方式

请求方法：GET

请求URL：/course/<int:course_id>/medias

请求参数：无

##### 返回示例

```bash
{
    "data": {
        "chapters": [
            {
                "create_at": "2020/08/28 10:43:43",
                "document_count": 1,
                "documents": [
                    {
                        "name": "my picture",
                        "type": "picture",
                        "upload_at": "2020/08/28 10:43:46",
                        "url": "http://127.0.0.1:5000/static/course/1/document/934c91d0-ff37-49d9-b2a0-e2169e157e6a.jpg",
                        "uuid": "934c91d0-ff37-49d9-b2a0-e2169e157e6a"
                    }
                ],
                "id": 1,
                "name": "test chapter",
                "update_at": "2020/08/28 10:43:46"
            }
        ],
        "count": 1,
        "have_next": 0,
        "have_prev": 0,
        "max_page": 1,
        "next_page": "http://127.0.0.1:5000/api/course/1/medias?page=2&per_page=20",
        "prev_page": "http://127.0.0.1:5000/api/course/1/medias?page=0&per_page=20"
    },
    "message": "succeed",
    "status": 2000
}
```



#### 创建章节

##### 请求方式

请求方法：POST

请求URL：/course/<int:cid>/chapters

请求参数：

| 请求参数     | 必须 | 类型 | 说明 |
| ------------ | ---- | ---- | ---- |
| chapter_name | 是   | str  |      |

##### 返回示例

```bash
{
    "data": "OK",
    "message": "succeed",
    "status": 2000
}
```



#### 获取课程章节列表

##### 请求方式

请求方法：GET

请求URL：/course/<int:cid>/chapters

请求参数：无

##### 返回示例

```bash
{
    "data": {
        "chapters": [
            {
                "create_at": "2020/08/28 10:43:43",
                "id": 1,
                "name": "test chapter",
                "update_at": "2020/08/28 10:43:46"
            }
        ],
        "count": 1,
        "have_next": 0,
        "have_prev": 0,
        "max_page": 1,
        "next_page": "http://127.0.0.1:5000/api/course/1/chapters?page=2&per_page=20",
        "prev_page": "http://127.0.0.1:5000/api/course/1/chapters?page=0&per_page=20"
    },
    "message": "succeed",
    "status": 2000
}
```



#### 获取某一文件信息

##### 请求方式

请求方法：GET

请求URL：/course/media/<str:media_id>

per_page默认20,page默认1

##### 返回示例

```bash
{
    "data": {
        "name": "my picture",
        "type": "picture",
        "upload_at": "2020/08/28 11:10:59",
        "url": "http://127.0.0.1:5000/static/course/1/document/bc7692fb-185a-467f-acd9-78db353aa870.jpg",
        "uuid": "bc7692fb-185a-467f-acd9-78db353aa870"
    },
    "message": "succeed",
    "status": 2000
}
```



## 课程讨论

#### 发布评论

##### 请求方式

请求方法：POST

请求URL：/course/<int:cid>/discussions/<string:discus_id>//comments

请求参数：

| 请求参数 | 必须 | 类型 | 说明           |
| -------- | ---- | ---- | -------------- |
| content  | 是   | str  |                |
| reply    | 否   | str  | 回复的评论的id |

##### 返回示例

```bash
{
    "data": {
        "author": {
            "avatar": "http://127.0.0.1:5000/static/avatars/user/banner14.jpg",
            "gender": "secret",
            "introduce": null,
            "nickname": "3927",
            "school": null,
            "self": "http://127.0.0.1:5000/api/student/1/info",
            "uid": 1
        },
        "content": "test_reply",
        "id": "7c20319e-9f92-456e-bc0b-d818ac08915c",
        "liked": false,
        "likes": 0,
        "post_at": "2020/08/28 11:27:08",
        "replies": [],
        "reply": "5260309c-a337-4ba0-b169-9cfa4bfb66d3"
    },
    "message": "succeed",
    "status": 2000
}
```



#### 发布讨论

##### 请求方式

请求URL：/course/<int:cid>/discussions

请求方法：POST

请求参数：

| 请求参数 | 必须 | 类型 | 说明 |
| -------- | ---- | ---- | ---- |
| content  | 是   | str  |      |

##### 返回示例：

```bash
{
    "data": {
        "collected": false,
        "collections": 0,
        "comments": [],
        "comments_count": 0,
        "content": "test discussion",
        "count": 0,
        "id": "9a41c21e-3d17-45ac-bd2e-24e7ffc2dc25",
        "post_at": "2020/08/28 11:27:04",
        "update_at": "2020/08/28 11:27:04",
        "user": {
            "avatar": "http://127.0.0.1:5000/static/avatars/user/banner14.jpg",
            "gender": "secret",
            "introduce": null,
            "nickname": "3927",
            "school": null,
            "self": "http://127.0.0.1:5000/api/student/1/info",
            "uid": 1
        }
    },
    "message": "succeed",
    "status": 2000
}
```

#### 获取讨论信息

##### 请求方式

请求URL：/course/<int:cid>/discussions/<str:discuss_id>

请求方法：GET

请求参数：无

##### 返回示例：

```bash
{
    "data": {
        "collected": false,
        "collections": 0,
        "comments": [
            {
                "author": {
                    "avatar": "http://127.0.0.1:5000/static/avatars/user/banner14.jpg",
                    "gender": "secret",
                    "introduce": null,
                    "nickname": "3927",
                    "school": null,
                    "self": "http://127.0.0.1:5000/api/student/1/info",
                    "uid": 1
                },
                "content": "test_comment",
                "id": "5260309c-a337-4ba0-b169-9cfa4bfb66d3",
                "liked": false,
                "likes": 0,
                "post_at": "2020/08/28 11:27:06",
                "replies": [
                    {
                        "author": {
                            "avatar": "http://127.0.0.1:5000/static/avatars/user/banner14.jpg",
                            "gender": "secret",
                            "introduce": null,
                            "nickname": "3927",
                            "school": null,
                            "self": "http://127.0.0.1:5000/api/student/1/info",
                            "uid": 1
                        },
                        "content": "test_reply",
                        "id": "7c20319e-9f92-456e-bc0b-d818ac08915c",
                        "liked": false,
                        "likes": 0,
                        "post_at": "2020/08/28 11:27:08",
                        "replies": [],
                        "reply": "5260309c-a337-4ba0-b169-9cfa4bfb66d3"
                    }
                ],
                "reply": null
            }
        ],
        "comments_count": 2,
        "content": "test discussion",
        "count": 1,
        "id": "9a41c21e-3d17-45ac-bd2e-24e7ffc2dc25",
        "post_at": "2020/08/28 11:27:04",
        "update_at": "2020/08/28 11:27:04",
        "user": {
            "avatar": "http://127.0.0.1:5000/static/avatars/user/banner14.jpg",
            "gender": "secret",
            "introduce": null,
            "nickname": "3927",
            "school": null,
            "self": "http://127.0.0.1:5000/api/student/1/info",
            "uid": 1
        }
    },
    "message": "succeed",
    "status": 2000
}
```

#### 获取课程讨论列表

##### 请求方式

请求URL：/course/<int:cid>/discussions

请求方法：GET

请求参数：无

##### 返回示例

```bash
{
    "data": {
        "count": 1,
        "discussions": [
            {
                "collected": false,
                "collections": 0,
                "content": "test discussion",
                "id": "9a41c21e-3d17-45ac-bd2e-24e7ffc2dc25",
                "post_at": "2020/08/28 11:27:04",
                "update_at": "2020/08/28 11:27:04",
                "user": {
                    "avatar": "http://127.0.0.1:5000/static/avatars/user/banner14.jpg",
                    "gender": "secret",
                    "introduce": null,
                    "nickname": "3927",
                    "school": null,
                    "self": "http://127.0.0.1:5000/api/student/1/info",
                    "uid": 1
                }
            }
        ],
        "have_next": 0,
        "have_prev": 0,
        "max_page": 1,
        "next_page": "http://127.0.0.1:5000/api/course/1/discussions?page=2&per_page=20",
        "prev_page": "http://127.0.0.1:5000/api/course/1/discussions?page=0&per_page=20"
    },
    "message": "succeed",
    "status": 2000
}
```

#### 获取讨论评论列表

##### 请求方式

请求URL：/course/<int:cid>/discussions/<str:discuss_id>/comments

请求方法：GET

请求参数：无

##### 返回示例

```bash
{
    "data": {
        "comments": [
            {
                "author": {
                    "avatar": "http://127.0.0.1:5000/static/avatars/user/banner14.jpg",
                    "gender": "secret",
                    "introduce": null,
                    "nickname": "3927",
                    "school": null,
                    "self": "http://127.0.0.1:5000/api/student/1/info",
                    "uid": 1
                },
                "content": "test_comment",
                "id": "5260309c-a337-4ba0-b169-9cfa4bfb66d3",
                "liked": false,
                "likes": 0,
                "post_at": "2020/08/28 11:27:06",
                "replies": [
                    {
                        "author": {
                            "avatar": "http://127.0.0.1:5000/static/avatars/user/banner14.jpg",
                            "gender": "secret",
                            "introduce": null,
                            "nickname": "3927",
                            "school": null,
                            "self": "http://127.0.0.1:5000/api/student/1/info",
                            "uid": 1
                        },
                        "content": "test_reply",
                        "id": "7c20319e-9f92-456e-bc0b-d818ac08915c",
                        "liked": false,
                        "likes": 0,
                        "post_at": "2020/08/28 11:27:08",
                        "replies": [],
                        "reply": "5260309c-a337-4ba0-b169-9cfa4bfb66d3"
                    }
                ],
                "reply": null
            }
        ],
        "count": 1,
        "have_next": 0,
        "have_prev": 0,
        "max_page": 1,
        "next_page": "http://127.0.0.1:5000/api/course/1/discussions/9a41c21e-3d17-45ac-bd2e-24e7ffc2dc25/comments?page=2&per_page=20",
        "prev_page": "http://127.0.0.1:5000/api/course/1/discussions/9a41c21e-3d17-45ac-bd2e-24e7ffc2dc25/comments?page=0&per_page=20"
    },
    "message": "succeed",
    "status": 2000
}
```

#### 获取评论信息

##### 请求方式

请求URL：/course/<int:cid>/comment/<str:comment_id>

请求方法：GET

请求参数：无

##### 返回示例

```bash
{
    "data": {
        "author": {
            "avatar": "http://127.0.0.1:5000/static/avatars/user/banner14.jpg",
            "gender": "secret",
            "introduce": null,
            "nickname": "3927",
            "school": null,
            "self": "http://127.0.0.1:5000/api/student/1/info",
            "uid": 1
        },
        "content": "test_comment",
        "id": "5260309c-a337-4ba0-b169-9cfa4bfb66d3",
        "liked": false,
        "likes": 0,
        "post_at": "2020/08/28 11:27:06",
        "replies": [
            {
                "author": {
                    "avatar": "http://127.0.0.1:5000/static/avatars/user/banner14.jpg",
                    "gender": "secret",
                    "introduce": null,
                    "nickname": "3927",
                    "school": null,
                    "self": "http://127.0.0.1:5000/api/student/1/info",
                    "uid": 1
                },
                "content": "test_reply",
                "id": "7c20319e-9f92-456e-bc0b-d818ac08915c",
                "liked": false,
                "likes": 0,
                "post_at": "2020/08/28 11:27:08",
                "replies": [],
                "reply": "5260309c-a337-4ba0-b169-9cfa4bfb66d3"
            }
        ],
        "reply": null
    },
    "message": "succeed",
    "status": 2000
}
```

#### 点赞评论

##### 请求方式

请求URL：/course/<int:cid>/comment/<str:comment_id>/like

请求方法：POST

请求参数：无

##### 返回示例

```bash
{
    "data": "OK",
    "message": "succeed",
    "status": 2000
}
```

#### 获取个人围观的讨论列表

##### 请求方式

请求URL：/course/discussions/collection

请求方法：GET

请求参数：无

##### 返回示例

```bash
{
    "data": {
        "count": 0,
        "discussions": [],
        "have_next": 0,
        "have_prev": 0,
        "max_page": 0,
        "next_page": "http://127.0.0.1:5000/api/course/discussions/collection?page=2&per_page=20",
        "prev_page": "http://127.0.0.1:5000/api/course/discussions/collection?page=0&per_page=20"
    },
    "message": "succeed",
    "status": 2000
}
```

#### 围观讨论

##### 请求方式

请求URL：/course/<int:cid>/discussions/<str:discuss_id>/collect

请求方法：POST

请求参数：无

##### 返回示例

```bash
{
    "data": "OK",
    "message": "succeed",
    "status": 2000
}
```

#### 首页推荐讨论列表

##### 请求方式

请求URL：/course/discussions/recommend

请求方法：GET

请求参数：无

##### 返回示例

```bash
{
    "data": {
        "count": 1,
        "discussions": [
            {
                "collected": false,
                "collections": 1,
                "content": "test discussion",
                "id": "9a41c21e-3d17-45ac-bd2e-24e7ffc2dc25",
                "post_at": "2020/08/28 11:27:04",
                "update_at": "2020/08/28 11:27:04",
                "user": {
                    "avatar": "http://127.0.0.1:5000/static/avatars/user/banner14.jpg",
                    "gender": "secret",
                    "introduce": null,
                    "nickname": "3927",
                    "school": null,
                    "self": "http://127.0.0.1:5000/api/student/1/info",
                    "uid": 1
                }
            }
        ]
    },
    "message": "succeed",
    "status": 2000
}
```



### 课程公告，签到

#### 发布公告

##### 请求方式

请求URL：/course/<int:id>/notices

请求方法：POST

请求参数：

| 请求参数 | 必须 | 类型 | 说明 |
| -------- | ---- | ---- | ---- |
| title    | 是   | str  |      |
| content  | 是   | str  |      |

##### 返回示例

```bash
{
    "data": {
        "content": "huanyin!",
        "create_at": "2020/08/28 10:43:34",
        "id": "ca92d93b-f4fc-42fc-ba47-d2dc02ced12d",
        "read": 0,
        "self": "http://127.0.0.1:5000/api/course/1/notices/ca92d93b-f4fc-42fc-ba47-d2dc02ced12d",
        "title": "kaikela!"
    },
    "message": "succeed",
    "status": 2000
}
```



#### 课程公告列表

##### 请求方式

请求URL：/course/<int:id>/notices

请求方法：GET

请求参数：无

##### 返回示例

```bash
{
    "data": {
        "count": 1,
        "have_next": 0,
        "have_prev": 0,
        "max_page": 1,
        "next_page": "http://127.0.0.1:5000/api/course/1/notices?page=2&per_page=20",
        "notices": [
            {
                "content": "huanyin!",
                "create_at": "2020/08/28 10:43:34",
                "id": "ca92d93b-f4fc-42fc-ba47-d2dc02ced12d",
                "read": 0,
                "self": "http://127.0.0.1:5000/api/course/1/notices/ca92d93b-f4fc-42fc-ba47-d2dc02ced12d",
                "title": "kaikela!"
            }
        ],
        "prev_page": "http://127.0.0.1:5000/api/course/1/notices?page=0&per_page=20"
    },
    "message": "succeed",
    "status": 2000
}
```



#### 某一公告信息

##### 请求方式

请求URL：/course/<int:id>/notices/<string:notice_id>

请求方法：GET

请求参数：无

##### 返回示例

```bash
{
    "data": {
        "content": "huanyin!",
        "create_at": "2020/08/28 10:43:34",
        "id": "ca92d93b-f4fc-42fc-ba47-d2dc02ced12d",
        "read": 0,
        "self": "http://127.0.0.1:5000/api/course/1/notices/ca92d93b-f4fc-42fc-ba47-d2dc02ced12d",
        "title": "kaikela!"
    },
    "message": "succeed",
    "status": 2000
}
```



#### 确认公告

##### 请求方式

请求URL：/course/<int:id>/notices/<string:notice_id>

请求方法：POST

请求参数：无

##### 返回示例

```bash
{
    "data": "OK",
    "message": "succeed",
    "status": 2000
}
```

#### 删除公告

##### 请求方式

请求URL：/course/<int:id>/notices/<string:notice_id>

请求方法：DELETE

请求参数：无

##### 返回示例

```bash
{
    "data": "OK",
    "message": "succeed",
    "status": 2000
}
```

#### 获取当前签到信息

##### 请求方式

请求URL：/course/<int:id>/commit

请求方法：GET

请求参数：无

##### 返回示例

```bash
#当前未存在签到
{
    "data": {
        "exist": 0
    },
    "message": "succeed",
    "status": 2000
}
# 当前存在签到
{
    "data": {
        "begin": 1598586442.9345322,
        "end": 1598586502.9345322,
        "exist": 1,
        "finish": 0,
        "finished": [],
        "id": "5b0895eb-7864-4bd1-95d8-993a3e1af47b",
        "unfinished": []
    },
    "message": "succeed",
    "status": 2000
}
```

#### 发布签到

##### 请求方式

请求URL：/course/<int:id>/commit

请求方法：POST

请求参数：

| 请求参数 | 必须 | 类型 | 说明         |
| -------- | ---- | ---- | ------------ |
| expires  | 1    | int  | 签到持续时间 |

##### 返回示例

```bash
{
    "data": {
        "begin": 1598586442.9345322,
        "end": 1598586502.9345322,
        "finished": [],
        "id": "5b0895eb-7864-4bd1-95d8-993a3e1af47b",
        "unfinished": []
    },
    "message": "succeed",
    "status": 2000
}
```

#### 进行签到

##### 请求方式

请求URL：/course/<int:cid>/commit

请求方法：PUT

请求参数：无

##### 返回示例

```bash
{
    "data": "OK",
    "message": "succeed",
    "status": 2000
}
```

#### 获取签到统计数据

##### 请求方式

请求URL：/course/<int:cid>/commit/statistics?commit_id=<str:commit_id>

请求方法：GET

请求参数：无

##### 返回示例

```bash
{
    "data": {
        "count": 1,
        "have_next": 0,
        "have_prev": 0,
        "items": [
            {
                "count_finished": 1,
                "count_unfinished": 0,
                "finish_rate": 1.0,
                "finished": [
                    "3927"
                ],
                "unfinished": []
            }
        ],
        "max_page": 1,
        "next_page": "http://127.0.0.1:5000/api/course/1/commit/statistics?page=2&per_page=20",
        "prev_page": "http://127.0.0.1:5000/api/course/1/commit/statistics?page=0&per_page=20"
    },
    "message": "succeed",
    "status": 2000
}
```
若未指定签到id则获取课程全部签到信息


### 课程作业

#### 发布作业

##### 请求方式

请求方法：POST

请求URL：/course/<int:course_id>/tasks

请求参数：

| 请求参数        | 必须 | 类型                | 说明             |
| --------------- | ---- | ------------------- | ---------------- |
| type            | 是   | （“test”， “exam”） | 选一个           |
| t_begin         | 是   | 时间戳              | 开始时间         |
| t_end           | 是   | 时间戳              | 截至时间         |
| name            | 是   | str                 | 作业名称         |
| ans_visible     | 是   | 0 or 1              | 答案是否可见     |
| problems        | 是   | object              | 问题，跟校赛一样 |
| problem + order | 否   | file                | 对应题号的文件   |

每个problem所需要参数：（这个跟校赛一样，未做改动）

| 请求参数      | 必须         | 类型                                                         | 说明   |
| ------------- | ------------ | ------------------------------------------------------------ | ------ |
| type          | 是           | （“select”, "blank", "subjective"）                          | 选一个 |
| content       | 是           | 若为选择题，则为一个包含text与options的字典，否则为一个字符串 |        |
| answer        | 选择填空必须 | 列表（论述题为字符串）                                       |        |
| answer_detail | 是           | str                                                          |        |
| max_score     | 否           | int                                                          | 分值   |
| order         | 是           | int                                                          | 题号   |

##### 返回示例

```bash
{
    "data": {
        "answer_visible": true,
        "create_at": "2020/08/28 12:01:46",
        "finished": false,
        "id": "41f418bc-7696-4c90-8c04-043b982ca2c6",
        "max_score": 280,
        "problems": [
            {
                "content": {
                    "options": [
                        "选项A",
                        "选项B",
                        "选项C"
                    ],
                    "text": "选择题文本（可为空）"
                },
                "create_at": "2020/08/28 12:01:46",
                "id": "ebb33216-7047-4480-a208-eede33a78a4d",
                "max_score": 5,
                "medias": [],
                "order": 1,
                "picture_exist": 1,
                "type": "select"
            },
            {
                "content": {
                    "options": [],
                    "text": "the answer for  2333 is ___"
                },
                "create_at": "2020/08/28 12:01:46",
                "id": "66614c24-ffb5-4dd2-9f2f-47772ff5ae1a",
                "max_score": 5,
                "medias": [],
                "order": 2,
                "picture_exist": 1,
                "type": "blank"
            },
            {
                "content": {
                    "options": [
                        "选项A",
                        "选项B",
                        "选项C"
                    ],
                    "text": "the answer for  2333 is ___"
                },
                "create_at": "2020/08/28 12:01:46",
                "id": "4e7d89ff-9efe-475b-ab59-eae00dfdf47c",
                "max_score": 90,
                "medias": [],
                "order": 3,
                "picture_exist": 1,
                "type": "subjective"
            },
            {
                "content": {
                    "options": [
                        "选项A",
                        "选项B",
                        "选项C"
                    ],
                    "text": "the answer for  2333 is ___"
                },
                "create_at": "2020/08/28 12:01:46",
                "id": "a67f72ec-040c-4239-8ce8-706f7fd0741a",
                "max_score": 90,
                "medias": [],
                "order": 4,
                "picture_exist": 1,
                "type": "subjective"
            },
            {
                "content": {
                    "options": [
                        "选项A",
                        "选项B",
                        "选项C"
                    ],
                    "text": "the answer for  2333 is ___"
                },
                "create_at": "2020/08/28 12:01:46",
                "id": "ebad7a60-ddf0-48c4-b9be-ccc85f3a6bd8",
                "max_score": 90,
                "medias": [
                    {
                        "name": "def9bf15-01bb-4d7c-b4e8-7adaf9ca8ccd",
                        "type": "picture",
                        "upload_at": "2020/08/28 12:01:46",
                        "url": "http://127.0.0.1:5000/static/problem/def9bf15-01bb-4d7c-b4e8-7adaf9ca8ccd.jpg",
                        "uuid": "def9bf15-01bb-4d7c-b4e8-7adaf9ca8ccd"
                    }
                ],
                "order": 5,
                "picture_exist": 1,
                "type": "subjective"
            }
        ],
        "self": "http://127.0.0.1:5000/api/course/task/41f418bc-7696-4c90-8c04-043b982ca2c6",
        "statistic": {
            "statistic_blank": {
                "count": 1,
                "sum": 5
            },
            "statistic_select": {
                "count": 1,
                "sum": 5
            },
            "statistic_subjective": {
                "count": 3,
                "sum": 270
            }
        },
        "task_name": "test_task",
        "time_begin": "1970/01/01 08:00:00",
        "time_end": "2020/08/28 00:07:59",
        "time_excess": true,
        "type": "test"
    },
    "message": "succeed",
    "status": 2000
}
```



#### 提交作业

##### 请求方式

请求方法：POST

请求URL：/course/task/<str:task_id>/submit

请求参数：

| 请求参数 | 必须 | 类型 | 说明         |
| -------- | ---- | ---- | ------------ |
| answers  | 是   | list | 包括许多回答 |

answers中每个answer所要具有的参数如下，任然跟校赛一样未改动

| 请求参数       | 必须 | 类型                       | 说明                       |
| -------------- | ---- | -------------------------- | -------------------------- |
| order          | 是   | int                        | 题号                       |
| content        | 否   | 多选题为列表，其它为字符串 | 答案内容                   |
| answer + order | 否   | file                       | 学生对应题号题目上传的文件 |

##### 返回示例

```bash
{
    "data": {
        "answers": [
            {
                "answer_at": "2020/08/28 12:07:02",
                "answer_detail": "可为空",
                "comment": null,
                "content": [
                    "A"
                ],
                "correct_answer": [
                    "A"
                ],
                "id": "655098bd-c0b7-423a-b79b-1de6d9b59599",
                "medias": [],
                "order": 1,
                "score": 5,
                "update_at": "2020/08/28 12:07:02"
            },
            {
                "answer_at": "2020/08/28 12:07:02",
                "answer_detail": "可为空",
                "comment": null,
                "content": [
                    "A",
                    ""
                ],
                "correct_answer": [
                    "A",
                    "3rd23"
                ],
                "id": "492e705b-cd02-4510-8909-aca04b757a82",
                "medias": [],
                "order": 2,
                "score": 2.5,
                "update_at": "2020/08/28 12:07:02"
            },
            {
                "answer_at": "2020/08/28 12:07:02",
                "answer_detail": "fuck you",
                "comment": null,
                "content": [
                    ""
                ],
                "correct_answer": [
                    "i do not know"
                ],
                "id": "1c4f81d4-beb6-43c1-932a-26609f999116",
                "medias": [
                    {
                        "name": "8cb05e79-0178-4aa1-b6b7-ba20a550771f",
                        "type": "picture",
                        "upload_at": "2020/08/28 12:07:02",
                        "url": "http://127.0.0.1:5000/static/answer/8cb05e79-0178-4aa1-b6b7-ba20a550771f.jpg",
                        "uuid": "8cb05e79-0178-4aa1-b6b7-ba20a550771f"
                    }
                ],
                "order": 3,
                "score": 0,
                "update_at": "2020/08/28 12:07:02"
            },
            {
                "answer_at": "2020/08/28 12:07:02",
                "answer_detail": "fuck you",
                "comment": null,
                "content": [
                    ""
                ],
                "correct_answer": [
                    "i do not know"
                ],
                "id": "06f8ac1f-73e9-49f1-8d45-ce3479c9e9fa",
                "medias": [],
                "order": 4,
                "score": 0,
                "update_at": "2020/08/28 12:07:02"
            },
            {
                "answer_at": "2020/08/28 12:07:02",
                "answer_detail": "fuck you",
                "comment": null,
                "content": [
                    ""
                ],
                "correct_answer": [
                    "i do not know"
                ],
                "id": "e3471bfe-2691-4968-9455-8d0a0bfa72a6",
                "medias": [],
                "order": 5,
                "score": 0,
                "update_at": "2020/08/28 12:07:02"
            }
        ],
        "create_at": "2020/08/28 12:07:02",
        "id": "45a57c4d-0f19-4e95-9c04-f01deb44c9fd",
        "score": 7.5,
        "status": false,
        "update_at": "2020/08/28 12:07:02"
    },
    "message": "succeed",
    "status": 2000
}
```



#### 批改作业

##### 请求方式

请求方法：POST

请求URL：/course/task/<str:task_id>/check_answer

请求参数：

| 请求参数       | 必须 | 类型 | 说明                         |
| -------------- | ---- | ---- | ---------------------------- |
| check_res      | 是   | list | 一个包含每一题批改结果的列表 |
| task_answer_id | 是   | str  | 批改的回答的id               |

列表中check_res每一项应该包含的参数为：

| 请求参数 | 必须 | 类型 | 说明     |
| -------- | ---- | ---- | -------- |
| order    | 是   | int  | 题号     |
| score    | 是   | int  | 分数     |
| comment  | 否   | str  | 教师点评 |

##### 返回示例

```bash
{
    "data": "OK",
    "message": "succeed",
    "status": 2000
}
```

#### 获取课程作业列表

##### 请求方式

请求方法：GET

请求URL：/course/<int:cid>/tasks

请求参数：无

##### 返回示例

```bash
{
    "data": {
        "count": 2,
        "have_next": 0,
        "have_prev": 0,
        "max_page": 1,
        "next_page": "http://127.0.0.1:5000/api/course/1/tasks?page=2&per_page=20",
        "prev_page": "http://127.0.0.1:5000/api/course/1/tasks?page=0&per_page=20",
        "tasks": [
            {
                "answer_visible": true,
                "create_at": "2020/08/28 12:01:46",
                "id": "41f418bc-7696-4c90-8c04-043b982ca2c6",
                "max_score": 280,
                "self": "http://127.0.0.1:5000/api/course/task/41f418bc-7696-4c90-8c04-043b982ca2c6",
                "task_name": "test_task",
                "time_begin": "1970/01/01 08:00:00",
                "time_end": "2020/08/28 00:07:59",
                "time_excess": true,
                "type": "test"
            },
            {
                "answer_visible": true,
                "create_at": "2020/08/28 12:06:57",
                "id": "d6ce9c4c-fc72-44a2-a224-5e9f5d41b889",
                "max_score": 280,
                "self": "http://127.0.0.1:5000/api/course/task/d6ce9c4c-fc72-44a2-a224-5e9f5d41b889",
                "task_name": "test_task",
                "time_begin": "1970/01/01 08:00:00",
                "time_end": "2052/05/06 01:54:39",
                "time_excess": false,
                "type": "test"
            }
        ]
    },
    "message": "succeed",
    "status": 2000
}
```

#### 获取某一课程作业

##### 请求方式

请求方法：GET

请求URL：/course/task/<str:task_id>

请求参数：无

##### 返回示例

```bash
{
    "data": {
        "answer_visible": true,
        "create_at": "2020/08/28 12:06:57",
        "id": "d6ce9c4c-fc72-44a2-a224-5e9f5d41b889",
        "max_score": 280,
        "self": "http://127.0.0.1:5000/api/course/task/d6ce9c4c-fc72-44a2-a224-5e9f5d41b889",
        "task_name": "test_task",
        "time_begin": "1970/01/01 08:00:00",
        "time_end": "2052/05/06 01:54:39",
        "time_excess": false,
        "type": "test"
    },
    "message": "succeed",
    "status": 2000
}
```

#### 获取某一课程作业我的回答

##### 请求方式

请求方法：GET

请求URL：/course/task/<str:task_id>/my_answer

请求参数：无

##### 返回示例

```bash
{
    "data": {
        "answers": [
            {
                "answer_at": "2020/08/28 12:07:02",
                "answer_detail": "可为空",
                "comment": null,
                "content": [
                    "A"
                ],
                "correct_answer": [
                    "A"
                ],
                "id": "655098bd-c0b7-423a-b79b-1de6d9b59599",
                "medias": [],
                "order": 1,
                "score": 5,
                "update_at": "2020/08/28 12:07:02"
            },
            {
                "answer_at": "2020/08/28 12:07:02",
                "answer_detail": "可为空",
                "comment": null,
                "content": [
                    "A",
                    ""
                ],
                "correct_answer": [
                    "A",
                    "3rd23"
                ],
                "id": "492e705b-cd02-4510-8909-aca04b757a82",
                "medias": [],
                "order": 2,
                "score": 2.5,
                "update_at": "2020/08/28 12:07:02"
            },
            {
                "answer_at": "2020/08/28 12:07:02",
                "answer_detail": "fuck you",
                "comment": "good",
                "content": [
                    ""
                ],
                "correct_answer": [
                    "i do not know"
                ],
                "id": "1c4f81d4-beb6-43c1-932a-26609f999116",
                "medias": [
                    {
                        "name": "8cb05e79-0178-4aa1-b6b7-ba20a550771f",
                        "type": "picture",
                        "upload_at": "2020/08/28 12:07:02",
                        "url": "http://127.0.0.1:5000/static/answer/8cb05e79-0178-4aa1-b6b7-ba20a550771f.jpg",
                        "uuid": "8cb05e79-0178-4aa1-b6b7-ba20a550771f"
                    }
                ],
                "order": 3,
                "score": 90,
                "update_at": "2020/08/28 12:09:02"
            },
            {
                "answer_at": "2020/08/28 12:07:02",
                "answer_detail": "fuck you",
                "comment": null,
                "content": [
                    ""
                ],
                "correct_answer": [
                    "i do not know"
                ],
                "id": "06f8ac1f-73e9-49f1-8d45-ce3479c9e9fa",
                "medias": [],
                "order": 4,
                "score": 10,
                "update_at": "2020/08/28 12:09:02"
            },
            {
                "answer_at": "2020/08/28 12:07:02",
                "answer_detail": "fuck you",
                "comment": null,
                "content": [
                    ""
                ],
                "correct_answer": [
                    "i do not know"
                ],
                "id": "e3471bfe-2691-4968-9455-8d0a0bfa72a6",
                "medias": [],
                "order": 5,
                "score": 23,
                "update_at": "2020/08/28 12:09:02"
            }
        ],
        "create_at": "2020/08/28 12:07:02",
        "id": "45a57c4d-0f19-4e95-9c04-f01deb44c9fd",
        "score": 130.5,
        "status": false,
        "update_at": "2020/08/28 12:09:02"
    },
    "message": "succeed",
    "status": 2000
}
```

#### 获取一份未批改的作业

##### 请求方式

请求方法：GET

请求URL：/course/task/<str:task_id>/check_answer

请求参数：无

##### 返回示例

```bash
{
    "data": {
        "answers": [
            {
                "answer_at": "2020/08/28 12:07:02",
                "answer_detail": "可为空",
                "comment": null,
                "content": [
                    "A"
                ],
                "correct_answer": [
                    "A"
                ],
                "id": "655098bd-c0b7-423a-b79b-1de6d9b59599",
                "medias": [],
                "order": 1,
                "score": 5,
                "update_at": "2020/08/28 12:07:02"
            },
            {
                "answer_at": "2020/08/28 12:07:02",
                "answer_detail": "可为空",
                "comment": null,
                "content": [
                    "A",
                    ""
                ],
                "correct_answer": [
                    "A",
                    "3rd23"
                ],
                "id": "492e705b-cd02-4510-8909-aca04b757a82",
                "medias": [],
                "order": 2,
                "score": 2.5,
                "update_at": "2020/08/28 12:07:02"
            },
            {
                "answer_at": "2020/08/28 12:07:02",
                "answer_detail": "fuck you",
                "comment": "good",
                "content": [
                    ""
                ],
                "correct_answer": [
                    "i do not know"
                ],
                "id": "1c4f81d4-beb6-43c1-932a-26609f999116",
                "medias": [
                    {
                        "name": "8cb05e79-0178-4aa1-b6b7-ba20a550771f",
                        "type": "picture",
                        "upload_at": "2020/08/28 12:07:02",
                        "url": "http://127.0.0.1:5000/static/answer/8cb05e79-0178-4aa1-b6b7-ba20a550771f.jpg",
                        "uuid": "8cb05e79-0178-4aa1-b6b7-ba20a550771f"
                    }
                ],
                "order": 3,
                "score": 90,
                "update_at": "2020/08/28 12:09:02"
            },
            {
                "answer_at": "2020/08/28 12:07:02",
                "answer_detail": "fuck you",
                "comment": null,
                "content": [
                    ""
                ],
                "correct_answer": [
                    "i do not know"
                ],
                "id": "06f8ac1f-73e9-49f1-8d45-ce3479c9e9fa",
                "medias": [],
                "order": 4,
                "score": 10,
                "update_at": "2020/08/28 12:09:02"
            },
            {
                "answer_at": "2020/08/28 12:07:02",
                "answer_detail": "fuck you",
                "comment": null,
                "content": [
                    ""
                ],
                "correct_answer": [
                    "i do not know"
                ],
                "id": "e3471bfe-2691-4968-9455-8d0a0bfa72a6",
                "medias": [],
                "order": 5,
                "score": 23,
                "update_at": "2020/08/28 12:09:02"
            }
        ],
        "create_at": "2020/08/28 12:07:02",
        "id": "45a57c4d-0f19-4e95-9c04-f01deb44c9fd",
        "score": 130.5,
        "status": false,
        "update_at": "2020/08/28 12:09:02"
    },
    "message": "succeed",
    "status": 2000
}
```

#### 获取作业统计数据

##### 请求方式

请求方法：GET

请求URL：/course/task/<str:task_id>/statistic?detail=<bool>

请求参数：无

##### 返回示例

```bash
{
    "data": {
        "average": 130.5,
        "fail_detail": [
            "3927"
        ],
        "finish_cnt": 1,
        "finish_rate": 0,
        "finished_detail": [
            "3927"
        ],
        "pass_cnt": 0,
        "pass_detail": [],
        "pass_rate": 0.0,
        "section_count": {
            "0": 0,
            "10": 0,
            "20": 0,
            "30": 0,
            "40": 0,
            "50": 0,
            "60": 0,
            "70": 0,
            "80": 0,
            "90": 0,
            "100": 0,
            "110": 0,
            "120": 0,
            "130": 1,
            "140": 0,
            "150": 0,
            "160": 0,
            "170": 0,
            "180": 0,
            "190": 0,
            "200": 0,
            "210": 0,
            "220": 0,
            "230": 0,
            "240": 0,
            "250": 0,
            "260": 0,
            "270": 0
        },
        "total_cnt": 0,
        "unfinished_detail": []
    },
    "message": "succeed",
    "status": 2000
}
```

#### 获取题目统计数据

##### 请求方式

请求方法：GET

请求URL：/course/task/<str:task_id>/statistic/problems?detail=<bool>&order=<int>

请求参数：无

##### 返回示例

```bash
{
    "data": {
        "average": 0,
        "correct_detail": [
            "3927"
        ],
        "correct_rate": 0,
        "fail_detail": [],
        "pass_detail": [
            "3927"
        ],
        "pass_rate": 0
    },
    "message": "succeed",
    "status": 2000
}
```

#### 删除作业

##### 请求方式

请求方法：DELETE

请求URL：/course/task/<str:task_id>

请求参数：无

##### 返回示例

```bash
{
    "data": "OK",
    "message": "succeed",
    "status": 2000
}
```



## 有关头像

#### 用户头像

##### 请求方式

请求方法：POST

请求URL：/avatars/user/<int:uid>

请求参数：

| 请求参数 | 必须 | 类型 | 说明 |
| -------- | ---- | ---- | ---- |
| avatar   | 是   | file |      |

##### 返回示例

无返回

##### 说明

用get方法请求该url可以获取用户头像，原理是请求该url后重定向到实际给出头像的url。但是请求用户信息时返回的信息中会有一个avatar参数对应其真实的URL，所以这个其实应该没什么用。



#### 课程头像

##### 请求方式

请求方法：POST

请求URL：/avatars/course/<int:cid>

请求参数：

| 请求参数 | 必须 | 类型 | 说明 |
| -------- | ---- | ---- | ---- |
| avatar   | 是   | file |      |

##### 返回示例

无返回

##### 说明

该URL的get方法同用户



## WebSocket

跟校赛一样

#### 加入房间

##### 需要参数：

cid:课程id, nickname:用户名

##### 请求示例：

```html
<button onclick=join_room()>join room1</button>

function join_room(){
        console.log("send begin")
        socket.emit('join_room', {'cid': '1', 'nickname': 'lin'})
        console.log("send end")
    }
```

##### 返回示例：

```bash
"3927"  # 就返回一个用户名
```



#### 离开房间

##### 需要参数：

cid:课程id, nickname:用户名

##### 请求示例：

```html
<button onclick=leave_room()>leave room1</button>

function leave_room(){
        console.log("send begin")
        socket.emit('leave_room', {'cid': '1', 'nickname': 'lin'})
        console.log("send end")
    }
```

##### 返回示例：

```bash
"3927"  # 就返回一个用户名
```



#### 发送消息

##### 需要参数：

cid:课程id, uid:用户id, content:消息内容

##### 请求示例：

```html
<button onclick=send_message()>new message</button>

function send_message(){
        console.log("send begin")
        socket.emit("send_message", {'cid': '1', 'uid': '1', 'content': 'test content'})
        console.log("send end")
    }
```

##### 返回示例:

```bash
{
	"content": "test content",
	"user": {
         "self": "user/1",
         "uid": 1,
         "nickname": "lin",
         "introduce": null,
         "gender": "male",
         "avatar": http://localhost/files/avatars/user/banner13.jpg,
         "school": "fzu", or null
    }
}
```

#### 获取系统消息

虽然我有写这个但是管理员发布系统消息我没写

##### 需要参数：

uid:用户id

##### 请求示例：

```html
<button onclick=send_message()>new message</button>

function send_message(){
        socket.emit("get_system_tips", {'uid': '1'})
    }
```

##### 返回示例

```bash
["system_mes1", "system_msg2"]
```