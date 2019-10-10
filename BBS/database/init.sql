CREATE TABLE IF NOT EXISTS `t_group`(
  `group_type` INT(1) NOT NULL DEFAULT 0,
  `group_name` VARCHAR(12) NOT NULL,
  `description` VARCHAR(40) NULL,
  UNIQUE (group_type, group_name)
);


CREATE TABLE IF NOT EXISTS `t_user`(
	`uid` INT(6) UNSIGNED AUTO_INCREMENT,
	`status` BOOLEAN NOT NULL DEFAULT TRUE,
	`created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	`updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	`username` VARCHAR(12) NOT NULL,
	`email`  VARCHAR(40) NULL,
	`phone` VARCHAR(11) NULL,
	`password` VARCHAR(40) NOT NULL,
	`point` INT(4) DEFAULT 0,
	`sex` BOOLEAN DEFAULT TRUE,
	`address` VARCHAR(60) NULL,
	`group_type` INT(1) NOT NULL DEFAULT 0,
	CONSTRAINT pk_user_uid PRIMARY KEY (uid),
	CONSTRAINT fk_user_group_group_type FOREIGN KEY (group_type) REFERENCES t_group(group_type),
	UNIQUE (uid, username, email, phone)
)AUTO_INCREMENT=100000;


CREATE TABLE IF NOT EXISTS `t_tag`(
	`tid` INT(6) UNSIGNED AUTO_INCREMENT,
	`created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	`updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	`status` BOOLEAN NOT NULL DEFAULT TRUE,
	`tag_name` VARCHAR(12) NOT NULL,
	CONSTRAINT pk_tag_tid PRIMARY KEY (tid),
	UNIQUE(tid)
)AUTO_INCREMENT=100000;


CREATE TABLE IF NOT EXISTS `t_question`(
	`qid` INT(6) UNSIGNED AUTO_INCREMENT,
	`status` BOOLEAN NOT NULL DEFAULT FALSE,
	`created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	`updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	`abstract` VARCHAR(40) NOT NULL,
	`content` VARCHAR(10240) NOT NULL,
	`view_count` INT NOT NULL DEFAULT 0,
	`answer_count` INT NOT NULL DEFAULT 0,
	`adopted_count` INT(1) NOT NULL DEFAULT 0,
	`uid` INT(6) UNSIGNED NOT NULL,
	`tid` INT(6) UNSIGNED NOT NULL,
	CONSTRAINT pk_question_qid PRIMARY KEY (qid),
	CONSTRAINT fk_question_user_uid FOREIGN KEY (uid) REFERENCES t_user (uid),
	CONSTRAINT fk_question_tag_tid FOREIGN KEY (tid) REFERENCES t_tag (tid),
	UNIQUE(qid, uid, tid)
)AUTO_INCREMENT=100000;


CREATE TABLE IF NOT EXISTS `t_answer`(
	`aid` INT(6) UNSIGNED AUTO_INCREMENT,
	`status` BOOLEAN NOT NULL DEFAULT FALSE,
	`created_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	`updated_at` TIMESTAMP DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP,
	`content` VARCHAR(10240) NOT NULL,
	`has_read` BOOLEAN NOT NULL DEFAULT FALSE,
 	`qid` INT(6) UNSIGNED NOT NULL,
	`uid` INT(6) UNSIGNED NOT NULL,
	CONSTRAINT pk_answer_aid PRIMARY KEY (aid),
	CONSTRAINT fk_answer_question_qid FOREIGN KEY (qid) REFERENCES t_question (qid) ON DELETE CASCADE ON UPDATE CASCADE,
	CONSTRAINT fk_answer_user_uid FOREIGN KEY (uid) REFERENCES t_user (uid),
	UNIQUE(aid, qid)
)AUTO_INCREMENT=100000;


ALTER TABLE t_group ADD INDEX idx_group(group_name(4));
ALTER TABLE t_user ADD INDEX idx_user(username(8), email(8), phone(8));
ALTER TABLE t_question ADD INDEX idx_question(abstract(8), content(8));
ALTER TABLE t_answer ADD INDEX idx_answer(content(8));
ALTER TABLE t_tag ADD INDEX idx_tag(tag_name(2));
ALTER TABLE t_answer ADD INDEX idx_answer_has_read(has_read(1));


INSERT INTO t_group(group_type, group_name, description) VALUES (
  0,
  'user',
  'normal user'
),(
  1,
  'admin',
  'admin user'
),(
  2,
  'superuser',
  'super admin user'
);


INSERT INTO t_user(username, email, password, group_type) VALUES (
	'hugo',
	'zhang8680@outlook.com',
	'18f3e922a1d1a9a140efbbe894bc829eeec260d8',
	2
);

INSERT INTO t_tag(tag_name) VALUES ('Python'), ('C#'), ('Docker');
