create table access
(
  id   int auto_increment
    primary key,
  name varchar(20) not null
);

create table alembic_version
(
  version_num varchar(32) not null
    primary key
);

create table endpoint
(
  id        int auto_increment
    primary key,
  name      varchar(50)  not null,
  url       varchar(100) not null,
  access_id int          not null,
  constraint endpoint_ibfk_1
    foreign key (access_id) references access (id)
);

create index access_id
  on endpoint (access_id);

create table permission
(
  id    int auto_increment
    primary key,
  name  varchar(50) null,
  type  varchar(20) null,
  value int         null
);

create index ix_permission_name
  on permission (name);

create table registry
(
  id        int auto_increment
    primary key,
  name      varchar(50)  not null,
  url       varchar(100) not null,
  access_id int          not null,
  constraint registry_ibfk_1
    foreign key (access_id) references access (id)
);

create index access_id
  on registry (access_id);

create table role
(
  id   int auto_increment
    primary key,
  name varchar(140) not null
);

create table user
(
  id            int auto_increment
    primary key,
  email         varchar(120) not null,
  password_hash varchar(128) not null,
  create_date   datetime     null,
  last_visit    datetime     null,
  active        tinyint(1)   null,
  role_id       int          null,
  constraint ix_user_email
    unique (email),
  constraint user_ibfk_1
    foreign key (role_id) references role (id)
);

create table container
(
  id          int auto_increment
    primary key,
  creator_id  int          not null,
  create_time datetime     null,
  access_id   int          not null,
  hash        varchar(255) not null,
  constraint container_ibfk_1
    foreign key (access_id) references access (id),
  constraint container_ibfk_2
    foreign key (creator_id) references user (id)
);

create index access_id
  on container (access_id);

create index creator_id
  on container (creator_id);

create table `group`
(
  id          int auto_increment
    primary key,
  name        varchar(200) not null,
  creator_id  int          null,
  create_time datetime     null,
  active      tinyint(1)   null,
  `desc`      varchar(255) null,
  constraint name
    unique (name),
  constraint group_ibfk_1
    foreign key (creator_id) references user (id)
);

create table container2group
(
  container_id int not null,
  group_id     int not null,
  primary key (container_id, group_id),
  constraint container2group_ibfk_1
    foreign key (container_id) references container (id),
  constraint container2group_ibfk_2
    foreign key (group_id) references `group` (id)
);

create index group_id
  on container2group (group_id);

create table endpoint2group
(
  endpoint_id int not null,
  group_id    int not null,
  primary key (endpoint_id, group_id),
  constraint endpoint2group_ibfk_1
    foreign key (endpoint_id) references endpoint (id),
  constraint endpoint2group_ibfk_2
    foreign key (group_id) references `group` (id)
);

create index group_id
  on endpoint2group (group_id);

create index creator_id
  on `group` (creator_id);

create table image
(
  id          int auto_increment
    primary key,
  creator_id  int          not null,
  create_time datetime     null,
  access_id   int          not null,
  hash        varchar(255) not null,
  constraint hash
    unique (hash),
  constraint image_ibfk_1
    foreign key (access_id) references access (id),
  constraint image_ibfk_2
    foreign key (creator_id) references user (id)
);

create index access_id
  on image (access_id);

create index creator_id
  on image (creator_id);

create table image2group
(
  image_id int not null,
  group_id int not null,
  primary key (image_id, group_id),
  constraint image2group_ibfk_1
    foreign key (group_id) references `group` (id),
  constraint image2group_ibfk_2
    foreign key (image_id) references image (id)
);

create index group_id
  on image2group (group_id);

create table network
(
  id          int auto_increment
    primary key,
  creator_id  int          not null,
  create_time datetime     null,
  access_id   int          not null,
  hash        varchar(255) not null,
  constraint network_ibfk_1
    foreign key (access_id) references access (id),
  constraint network_ibfk_2
    foreign key (creator_id) references user (id)
);

create index access_id
  on network (access_id);

create index creator_id
  on network (creator_id);

create table network2group
(
  network_id int not null,
  group_id   int not null,
  primary key (network_id, group_id),
  constraint network2group_ibfk_1
    foreign key (group_id) references `group` (id),
  constraint network2group_ibfk_2
    foreign key (network_id) references network (id)
);

create index group_id
  on network2group (group_id);

create table registry2group
(
  registry int not null,
  `group`  int not null,
  primary key (registry, `group`),
  constraint registry2group_ibfk_1
    foreign key (`group`) references `group` (id),
  constraint registry2group_ibfk_2
    foreign key (registry) references registry (id)
);

create index `group`
  on registry2group (`group`);

create index role_id
  on user (role_id);

create table user2group
(
  user_id  int not null,
  group_id int not null,
  primary key (user_id, group_id),
  constraint user2group_ibfk_1
    foreign key (group_id) references `group` (id),
  constraint user2group_ibfk_2
    foreign key (user_id) references user (id)
);

create index group_id
  on user2group (group_id);

create table user2permission
(
  user_id       int not null,
  permission_id int not null,
  primary key (user_id, permission_id),
  constraint user2permission_ibfk_1
    foreign key (permission_id) references permission (id),
  constraint user2permission_ibfk_2
    foreign key (user_id) references user (id)
);

create index permission_id
  on user2permission (permission_id);

create table volume
(
  id          int auto_increment
    primary key,
  creator_id  int          not null,
  create_time datetime     null,
  access_id   int          not null,
  hash        varchar(255) not null,
  constraint volume_ibfk_1
    foreign key (access_id) references access (id),
  constraint volume_ibfk_2
    foreign key (creator_id) references user (id)
);

create index access_id
  on volume (access_id);

create index creator_id
  on volume (creator_id);

create table volume2group
(
  volume_id int not null,
  group_id  int not null,
  primary key (volume_id, group_id),
  constraint volume2group_ibfk_1
    foreign key (group_id) references `group` (id),
  constraint volume2group_ibfk_2
    foreign key (volume_id) references volume (id)
);

create index group_id
  on volume2group (group_id);


