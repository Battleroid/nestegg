CREATE DATABASE IF NOT EXISTS nestegg;
CREATE USER 'nestegg'@'localhost' IDENTIFIED BY 'nestegg';
GRANT ALL PRIVILEGES ON nestegg.* TO 'nestegg'@'localhost';
FLUSH PRIVILEGES;
