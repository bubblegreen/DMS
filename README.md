# DMS
A Docker Management System

#开发配置
###安装依赖
1、pip install -r requirement.txt

###创建.env文件
* DATABASE_URL= ：数据库连接信息，eg. root:test@localhost:3306
* MAIL_SERVER= ：邮箱服务地址，eg. smtp.qiye.aliyun.com
* MAIL_USERNAME= ：邮箱用户名，eg. xuhang@aisino.com
* MAIL_PASSWORD= ：邮箱密码
* SESSION_TIMEOUT= ：session超时时间，单位分钟，eg. 60

###建立数据库步骤
1、flask db init \
2、flask db migrate -m "create tables" \
3、flask db upgrade

###数据库交互
flask shell

###运行
flask run

#部署
###配置docker-compose.yml文件
1、db的配置  
* MYSQL_ROOT_PASSWORD：root的密码  
* MYSQL_DATABASE：数据库名  
* ports："*host-port*:3306"

2、web的配置
* SECRET_KEY：密匙，自定义的字符串，用于session加密（可选）
* DATABASE_URL：数据库链接串，root:*dbpwd*@db:3306，只需配置数据库密码（同db设置中的MYSQL_ROOT_PASSWORD）
* MAIL_SERVER：邮件服务地址
* MAIL_USERNAME：邮件用户名
* MAIL_PASSWORD：邮件密码
* ADMIN：预置的管理员邮箱，用户注册时，如果与该设置一致，该用户激活时自动设置为超级管理员
* SESSION_TIMEOUT：session超时时间，单位分钟（可选，默认60）

3、networks的配置
* 如果想在swarm集群中使用，将driver由bridge改为overlay

4、服务的创建、启动、停止及删除
* 创建：docker-compose up -d
* 停止：docker-compose stop
* 启动：docker-compose start
* 删除：docker-compose down

###Endpoint配置  
1、开启docker remote api
* 修改/lib/systemd/system/docker.service文件，去掉ExecStart=/usr/bin/dockerd -H fd:// --containerd=/run/containerd/containerd.sock中的"-H fd://"部分
* 在/etc/docker/daemon.json文件中添加{"hosts": ["tcp://0.0.0.0:2375", "unix:///var/run/docker.sock"]}
