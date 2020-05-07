FROM python:3.7.3-alpine3.10
LABEL author='xuhang<xuhang@aisino.com>'
RUN mkdir -p /opt/app/logs && mkdir /opt/app/temp_folder && mkdir /opt/app/app && apk add git
COPY *.py requirements.txt /opt/app/
COPY app /opt/app/app
WORKDIR /opt/app
RUN pip install -r requirements.txt -i http://mirrors.aliyun.com/pypi/simple --trusted-host mirrors.aliyun.com
VOLUME /opt/app/logs
ENV SECRET_KEY=com.aisino.testcenter.testcenter3093 \
    SESSION_TIMEOUT=60 \
    DATABASE_URL=root:test@192.168.23.58:3306 \
    MAIL_SERVER=smtp.qiye.aliyun.com \
    MAIL_USERNAME=xuhang@aisino.com \
    MAIL_PASSWORD=Xu810823 \
    ADMIN=xuhang@aisino.com
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5555", "dms:app"]
