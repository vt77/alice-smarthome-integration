DROP TABLE IF EXISTS devices;
CREATE TABLE `devices` (
  `device_id` int(13) NOT NULL AUTO_INCREMENT,
  `user_id` int(13) NOT NULL,
  `name` VARCHAR(32) NOT NULL,
  `description` VARCHAR(32) NOT NULL,  
  `room` VARCHAR(32) NOT NULL,
  `device_type` VARCHAR(32) NOT NULL,
  `capabilities` VARCHAR(256) NOT NULL,
  `properties` VARCHAR(256) NOT NULL,
  `device_info` VARCHAR(256) NOT NULL,
  `custom_data` VARCHAR(128) NOT NULL,
  PRIMARY KEY (device_id)
) ENGINE=MyISAM DEFAULT CHARSET=utf8;

GRANT ALL ON  yandex.devices TO 'yd-operator'@'localhost';


