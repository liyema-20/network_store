/* Author: Liyema Kota
Date: 6/03/2023
Function: Creating the database to be used by python programming project 2
*/

DROP DATABASE IF EXISTS network_store;
CREATE DATABASE network_store;
USE network_store;

CREATE TABLE customers(
	custID INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    fname VARCHAR(40) NOT NULL,
    sname VARCHAR(40) NOT NULL,
    address VARCHAR(40) NOT NULL,
    phone VARCHAR(10) NOT NULL UNIQUE
);

CREATE TABLE items(
	itemID INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    iname VARCHAR(50) NOT NULL,
    descrip VARCHAR(100) NOT NULL,
    price FLOAT NOT NULL,
    count INT NOT NULL
);

CREATE TABLE invoices(
	invoiceID INT PRIMARY KEY AUTO_INCREMENT NOT NULL,
    custID INT NOT NULL,
    dateBought DATE NOT NULL,
    totalPrice VARCHAR(10) NOT NULL,
    FOREIGN KEY (custID) REFERENCES customers (custID)
);


	