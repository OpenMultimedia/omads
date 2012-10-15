CREATE TABLE banner (
    id INT(11) NOT NULL AUTO_INCREMENT,
    medium VARCHAR(20),
    zone VARCHAR(2),
    file VARCHAR(255),
    link VARCHAR(255),
    created_at DATETIME,
    clicks INT(11),
    views INT(11),
    PRIMARY KEY (id)
);