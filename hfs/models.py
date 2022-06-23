import re
import time
from urllib.parse import unquote

from mail_gw import Account as TempMail
from requests import Session

from hfs.utils import generate_random_string


class Account:
    logged_in: bool = False  # 是否已登录
    email: str = None  # 当前好分数账号邮箱地址
    password: str = None  # 当前好分数账号密码
    session: Session = None  # requests会话
    student_data: dict = None  # 当前学生信息
    exams_data: list = None  # 考试列表

    def __init__(self):
        # 初始化session
        self.session = Session()
        self.session.headers.update({
            'User-Agent':
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/101.0.0.0 Safari/537.36',
            'Origin': 'https://www.haofenshu.com',
            'Referer': 'https://www.haofenshu.com/',
        })

    def login(self, email, password):
        '''
            直接登录已有账号（必须是学生版）
            @param email: 邮箱地址
            @param password: 密码
        '''
        r = self.session.post(
            'https://hfs-be.yunxiao.com/v2/users/sessions',
            data={
                'loginName': email,
                'password': password,
                'rememberMe': 2,
                'roleType': 1
            },
        )
        self.email = email
        self.password = password
        self.logged_in = r.status_code == 200

    def register(self,
                 studentName,
                 xuehao,
                 schoolName: str = None,
                 password: str = generate_random_string(8)):
        '''
            提供学生姓名和学号，自动使用临时邮箱注册、验证并登录好分数账号，返回生成账号的邮箱地址和密码。
            @param studentName: 学生姓名
            @param xuehao: 学号
            @param schoolName: 学校名称，可不填，用于对重名重学号的学生进行区分，若要填写请务必先抓包确认学校名称是否正确！
            @param password: 指定生成的学生账号设置的密码，可不填，若不填则自动生成随机密码
            返回值：元组(邮箱地址，密码)
        '''
        temp_mail = TempMail('hfs' + xuehao + generate_random_string(6),
                             password)
        r = self.session.post(
            'https://hfs-be.yunxiao.com/v2/native-users/verification-email',
            data={
                'email': temp_mail.address,
                'password': password,
                'roleType': 1
            },
        )

        # 获取验证邮件并验证
        time.sleep(5)
        r = None
        while r is None:
            try:
                r = temp_mail.get_message()
            except IndexError:
                time.sleep(5)
        ver_url = re.findall(r'>(http://www.haofenshu.com/.*?)<', r['html'][0])
        ver_code = re.findall(r'mailToken=(.*?)&', ver_url)[0]
        ver_code = unquote(ver_code, 'utf-8')
        r = self.session.post(
            'https://hfs-be.yunxiao.com/v2/native-users/activation',
            data={
                'deviceType': 3,
                'verificationType': 1,
                'verificationEmailToken': ver_code,
            },
        )
        self.email = temp_mail.address
        self.password = password

        # 查找并绑定学生
        r = self.session.get(
            'https://hfs-be.yunxiao.com/v2/users/matched-students',
            params={
                'roleType': '1',
                'identityType': '1',
                'identityCode': xuehao,
                'studentName': studentName
            }).json()
        studentId = ''
        if schoolName:
            for i in r['data']['students']:
                if schoolName in i['schoolName']:
                    studentId = i['studentId']
                    break
        else:
            studentId = r['data']['students'][0]['studentId']

        r = self.session.put(
            'https://hfs-be.yunxiao.com/v2/users/bind-student',
            data={
                'identityCode': xuehao,
                'identityType': '1',
                'studentId': studentId
            },
        )

        self.logged_in = True
        return self.email, self.password

    @property
    def student(self):
        '''
            获取当前学生信息。首次取值时会自动获取并缓存。
            @return studentId: 学生ID（好分数生成的唯一ID，不同于学号）
            @return studentName: 学生姓名
            @return schoolName: 学校名称
            @return xuehao: 学号
            @return grade: 年级
            @return className: 班级（导师姓名）
        '''
        assert self.logged_in, '获取学生信息前请先登录账号！'
        if self.student_data is None:
            r = self.session.get(
                'https://hfs-be.yunxiao.com/v2/user-center/user-snapshot'
            ).json()
            data = r['data']['linkedStudent']
            self.student_data = {
                i: data[i]
                for i in ('studentId', 'studentName', 'schoolName', 'grade',
                          'className')
            }
            self.student_data['xuehao'] = data['xuehao'][0]
        return self.student_data

    @property
    def exams(self):
        '''
            获取当前学生的考试列表。首次取值时会自动获取并缓存。
        '''
        assert self.logged_in, '获取考试列表前请先登录账号！'
        if self.exams_data is None:
            r = self.session.get(
                'https://hfs-be.yunxiao.com/v3/exam/list?start=-1').json()
            self.exams_data = r['data']['list']
        return self.exams_data

    def get_exam(self, latest=0):
        '''
            获取当前学生最近的第latest次考试，默认为最近一次考试。
            @param latest: 要获取的考试编号（0表示最近的一次，1表示第二近的一次，以此类推），默认为最近一次考试。
        '''
        assert self.logged_in, '获取考试详情前请先登录账号！'
        return Exam(self, self.exams[latest]['examId'])

    def __str__(self):
        '''
            示例值：'12345678-张三' 或 '未登录'
        '''
        if self.logged_in:
            return f'{self.student["xuehao"]}-{self.student["studentName"]}'
        else:
            return '未登录'


class Exam:
    account: Account = None  # 考试所属账号
    examId: int = None  # 考试ID
    data: dict = None  # 考试详细数据
    papers_data: dict = None  # 考试试卷数据字典，key为试卷名称，value为试卷对象

    @property
    def session(self):
        return self.account.session

    def __init__(self, account: Account, examId: int):
        '''
            初始化考试对象，自动获取考试详情。
            @param account: 账号对象
            @param examId: 考试编号
        '''
        self.account = account
        self.examId = examId
        r = self.session.get(
            f'https://hfs-be.yunxiao.com/v3/exam/{examId}/overview').json()
        self.data = r['data']

    @property
    def papers(self):
        '''
            获取考试的试卷列表。首次取值时会自动获取并缓存。
            返回值为一个字典，key为试卷名称，value为试卷对象。
        '''
        if self.papers_data is None:
            self.papers_data = {}
            for i in self.data['papers']:
                self.papers_data[i['name']] = Paper(self, i)
        return self.papers_data

    def __str__(self):
        '''
            示例值：'[12345678-张三]秋季学期期末考试'
        '''
        return f'[{self.account}]{self.data["name"]}'


class Paper:
    account: Account = None  # 试卷所属账号
    exam: Exam = None  # 试卷所属考试
    paperData: dict = None  # 试卷详细数据
    paperId: int = None  # 试卷ID
    questions_data: list = None  # 试卷题目数据列表
    pictures_data: list = None  # 答题卡图片URL列表

    @property
    def session(self):
        return self.account.session

    def __init__(self, exam: Exam, paperData: dict):
        self.exam = exam
        self.account = exam.account
        self.paperData = paperData
        self.paperId = paperData['paperId']

    def questions(self):
        '''
            获取试卷的题目列表。首次取值时会自动获取并缓存。
            该接口返回好分数原生数据，未进行优化，实用性不高。
        '''
        if self.questions_data is None:
            r = self.session.get(
                f'https://hfs-be.yunxiao.com/v3/exam/{self.exam.examId}/papers/{self.paperId}/question-detail'
            ).json()
            self.questions_data = r['data']['questionList']
        return self.questions_data

    @property
    def pictures(self):
        '''
            获取答题卡的图片列表。首次取值时会自动获取并缓存。
            返回值：一个列表，每个元素为字符串，表示图片URL。
        '''
        if self.pictures_data is None:
            r = self.session.get(
                f'https://hfs-be.yunxiao.com/v3/exam/{self.exam.examId}/papers/{self.paperId}/answer-picture'
            ).json()
            self.pictures_data = r['data']['url']
        return self.pictures_data

    def save_pictures(self, path: str):
        '''
            保存该试卷所有答题卡的图片到指定路径。
            @param path: 文件保存路径
            文件命名格式：
        '''
        for i in range(len(self.pictures)):
            r = self.session.get(self.pictures[i])
            with open(f'{path}/{self.paperData["name"]}-{i+1}.png', 'wb') as f:
                f.write(r.content)

    def __str__(self):
        '''
            示例值：'{[12345678-张三]秋季学期期末考试}-语文'
        '''
        return f'{{{self.exam}}}-{self.paperData["name"]}'


if __name__ == '__main__':
    ...
