DROP TABLE IF EXISTS users;
CREATE TABLE `users` (
  `user_id` int(13) NOT NULL AUTO_INCREMENT,
  `nickname` VARCHAR(13) NOT NULL,
  `password` VARCHAR(32) NOT NULL,  
  `balance` INT NOT NULL DEFAULT 0,
  `referal` INT NOT NULL DEFAULT 0,
  `jwtid` VARCHAR(13) NOT NULL DEFAULT '',
  `registred` DATETIME NOT NULL,
  `last_seen` TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP, 
  PRIMARY KEY (user_id),
  CONSTRAINT `nickname_idx` UNIQUE (`nickname`)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

GRANT UPDATE(jwtid,last_seen) ON  yandex.users TO 'yd-operator'@'localhost';

INSERT INTO users VALUES(100,'iothome','d57143a6518d08962b817d3f98a2d391',0,0,'',NOW(),NULL);

DROP TABLE IF EXISTS oauth_keys;
CREATE TABLE `oauth_keys` (
  `key_id` int(13) NOT NULL AUTO_INCREMENT,
  `user_id` int(13) NOT NULL,
  `token` VARCHAR(128),
  `issued` DATETIME NOT NULL,
  `expired` DATETIME NOT NULL,
  `refresh` VARCHAR(128)
)

GRANT ALL ON  yandex.oauth_keys TO 'yd-operator'@'localhost';


