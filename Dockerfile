FROM python:3.7.3-alpine3.10
LABEL author='xuhang<xuhang@aisino.com>'
RUN mkdir -p /opt/app
COPY app logs temp_folder *.py requirements.txt /opt/app/
WORKDIR /opt/app
RUN pip install -r requirements -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
VOLUME /opt/app/logs
ENV SECRET_KEY=com.aisino.testcenter.testcenter3093 \
    SESSION_TIMEOUT=60 \
    DATABASE_URL=root:testcenter@db:3306 \
    MAIL_SERVER=smtp.qiye.aliyun.com
    # MAIL_USERNAME=
    # MAIL_PASSWORD=
    # ADMIN=
CMD ["gunicorn", "-w", "4", "-b", "127.0.0.1:5555", "mng:app"]
