FROM python:3.7.3-alpine3.10
LABEL author='xuhang<xuhang@hotmail.com>'
RUN mkdir -p /opt/app/logs && mkdir /opt/app/temp_folder && mkdir /opt/app/app && apk add git
COPY *.py requirements.txt /opt/app/
COPY app /opt/app/app
WORKDIR /opt/app
RUN pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
#RUN flask db init && flask db migrate && flask db upgrade && flask generate init
VOLUME /opt/app/logs
ENV SECRET_KEY=com.testcenter.testcenter3093 \
    SESSION_TIMEOUT=60 \
    DATABASE_URL=mysql+pymysql://root:test@localhost:3306/docker \
    MAIL_SERVER=smtp.qiye.aliyun.com \
    MAIL_USERNAME= \
    MAIL_PASSWORD= \
    ADMIN=
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5555", "dms:app"]
