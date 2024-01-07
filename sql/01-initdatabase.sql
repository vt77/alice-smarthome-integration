CREATE DATABASE yandex;
SET OLD_PASSWORDS=0;

CREATE USER 'yd-admin'@'localhost' IDENTIFIED BY 'dfh5678djeh3mdj44d';
CREATE USER 'yd-operator'@'localhost' IDENTIFIED BY '4dfg4334fscdfsd234d';


GRANT ALL PRIVILEGES ON yandex.* TO 'yd-admin'@'localhost';
GRANT SELECT ON  yandex.* TO 'yd-operator'@'localhost';

FLUSH PRIVILEGES;
