DROP DATABASE IF EXISTS pychat;
CREATE DATABASE pychat;

USE pychat;

CREATE TABLE users (
	id INT not null AUTO_INCREMENT,
	username VARCHAR(50) NOT NULL,
	password VARCHAR(300) NOT NULL,
	email VARCHAR(100) NOT NULL,
	PRIMARY KEY (id)
);

CREATE TABLE friends (
	id integer auto_increment not null,
	user1_id integer not null,
	user2_id integer not null,
	primary key (id)
);

CREATE TABLE groups (
	id integer auto_increment not null,
	owner integer not null,
	primary key (id),
	foreign key (owner) references users(id)
);

CREATE TABLE messages (
	id integer auto_increment not null,
	groupid integer not null,
	sent_userid integer not null,
	content VARCHAR(1000),
	primary key (id),
	foreign key (groupid) references groups(id),
	foreign key (sent_userid) references users(id)
);



