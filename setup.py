from setuptools import setup

setup(
    name='haofs',
    version='0.1',
    description='好分数(https://www.haofenshu.com/)爬虫',
    url="https://github.com/Danny-Yxzl/haofs",
    author="Yixiangzhilv",
    author_email="mail@yixiangzhilv.com",
    classifiers=[
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10"
    ],
    keywords="API sdk spider",
    install_requires=["requests", "mail_gw"],
    packages=["hfs"],
    project_urls={
        "Bug Reports": "https://github.com/Danny-Yxzl/haofs/issues",
        "Say Thanks!": "https://www.yixiangzhilv.com/",
        "Source": "https://github.com/Danny-Yxzl/haofs",
    },
)
