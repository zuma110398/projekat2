CREATE SCHEMA IF NOT EXISTS `bolnica2` DEFAULT CHARACTER SET utf8 ;
USE `bolnica2` ;


CREATE TABLE odjeli (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ime VARCHAR(255) NOT NULL
);


CREATE TABLE doktori (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ime VARCHAR(255) NOT NULL,
    prezime VARCHAR(255) NOT NULL,
    odjel_id INT,
    FOREIGN KEY (odjel_id) REFERENCES odjeli(id)
);


CREATE TABLE pacijenti (
    id INT AUTO_INCREMENT PRIMARY KEY,
    ime VARCHAR(255) NOT NULL,
    prezime VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    password varchar(255) DEFAULT '',
    broj_telefona VARCHAR(20) NOT NULL
);


CREATE TABLE termini (
    id INT AUTO_INCREMENT PRIMARY KEY,
    doktor_id INT,
    pacijent_id INT,
    termin_date DATETIME NOT NULL,
    FOREIGN KEY (doktor_id) REFERENCES doktori(id),
    FOREIGN KEY (pacijent_id) REFERENCES pacijenti(id)
);


CREATE TABLE medicinski_kartoni (
    id INT AUTO_INCREMENT PRIMARY KEY,
    pacijent_id INT,
    stanje TEXT NOT NULL,
    lijek TEXT NOT NULL,
    FOREIGN KEY (pacijent_id) REFERENCES pacijenti(id)
);

