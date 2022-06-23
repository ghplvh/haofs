# 好分数爬虫

## 简介

这是一个[好分数](https://www.haofenshu.com/)网站的爬虫。可用于爬取好分数的总成绩、各科成绩、答题卡图片等。

与一般的爬虫相比，该项目**支持根据学生姓名和学号自动使用临时邮箱生成账号！**

## 安装

使用 `pip` 安装：

```bash
pip3 install haofs
```

## 使用示例

```python
# 导入库
from haofs import Account

# 创建账号对象
student = Account()

# 初始化
# 方式1：直接输入好分数学生账号邮箱和密码
student.login('admin@haofenshu.com', 'password')
# 方式2：输入学生姓名和学号，自动生成邮箱和密码
# @param schoolName 学校名称，可不填，用于对重名重学号的学生进行区分，若要填写请务必先抓包确认学校名称是否正确！
# @param password: 指定生成的学生账号设置的密码，可不填，若不填则自动生成随机密码
email, password = student.register('张三', '12345678', schoolName='清华大学', password='password')

# 获取学生详细信息，包括姓名、学号、年级、班级（导师班）等
print(student.student)

# 获取考试列表
print(student.exams)

# 获取一次考试的考试对象
# @param latest: 要获取的考试编号（0表示最近的一次，1表示第二近的一次，以此类推），默认为最近一次考试。
exam = student.get_exam(0)
# 亦可直接通过考试编号获取考试对象
# from haofs import Exam
# exam = Exam(student, student.exams[0]['examId'])

# 获取考试详细信息，包括考试ID、考试名称、考试时间、考试成绩、满分、排名等
print(exam.data)

# 获取考试的试卷信息
print(exam.papers)
# {'语文': <hfs.models.Paper object at 0x01>, '数学': <hfs.models.Paper object at 0x02>, '英语': <hfs.models.Paper object at 0x03>, ...}

# 获取一张试卷的试卷对象
paper = exam.papers['语文']

# 获取该试卷的答题卡图片URL列表
print(paper.pictures)  # ['http://...', 'http://...', ...]
# 直接保存答题卡到本地文件夹
paper.save_pictures('/path/to/save/')

# 获取该试卷的所有试题信息
print(paper.questions)
# 该接口返回值为未经优化的好分数原生数据，数据量巨大，且通常无需爬取具体试题信息，不建议使用。
```

## 已知问题

我们使用 `mail_gw` 库生成临时邮箱，该库依赖 [mail.gw](https://mail.gw/en/)，该网站受中国网络长城影响响应速度较慢。

## 联系方式

[mail@yixiangzhilv.com](mailto:mail@yixiangzhilv.com)
