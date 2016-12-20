USE pychat;
Drop table if exists group_members_list;
CREATE TABLE group_members_list (
	id INT NOT NULL AUTO_INCREMENT,
	user_id INT NOT NULL,
	groupid INT NOT NULL,
	Primary Key (id),
	Foreign key (user_id) references users(id),
	Foreign key (groupid) references groups(id)
);
