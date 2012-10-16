CREATE TABLE banner (
    id INT(11) NOT NULL AUTO_INCREMENT,
    medium VARCHAR(50) NOTNULL,
    zone VARCHAR(2),
    subzone VARCHAR(10) DEFAULT '',
    file VARCHAR(255),
    link VARCHAR(255) DEFAULT '',
    link_mode int(11) DEFAULT 0,
    created_at DATETIME,
    clicks INT(11) DEFAULT 0,
    views INT(11) DEFAULT 0,
    weight INT(11) DEFAULT 50,
    PRIMARY KEY (id)
);