-- ============================================================
--  ApexCare ERP — Database Schema
--  Run this file once to initialise the database.
-- ============================================================

CREATE DATABASE IF NOT EXISTS apexcare_erp
    CHARACTER SET utf8mb4
    COLLATE utf8mb4_unicode_ci;

USE apexcare_erp;

-- ----------------------------------------------------------
-- AUTH
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS users (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    username   VARCHAR(50)  NOT NULL UNIQUE,
    password   VARCHAR(255) NOT NULL,
    created_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

-- Default admin (username: admin | password: admin123)
INSERT IGNORE INTO users (username, password) VALUES ('admin', 'admin123');

-- ----------------------------------------------------------
-- HOSPITAL MODULE
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS patients (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    age        INT          NOT NULL,
    disease    VARCHAR(150) NOT NULL,
    contact    VARCHAR(20)  NOT NULL,
    created_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS doctors (
    id             INT AUTO_INCREMENT PRIMARY KEY,
    name           VARCHAR(100) NOT NULL,
    qualification  VARCHAR(100) NOT NULL,
    specialization VARCHAR(100) NOT NULL,
    experience     INT          NOT NULL,
    created_at     TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS appointments (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    patient_id INT         NOT NULL,
    doctor_id  INT         NOT NULL,
    date       DATE        NOT NULL,
    status     VARCHAR(50) NOT NULL DEFAULT 'Pending',
    created_at TIMESTAMP   DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (patient_id) REFERENCES patients(id) ON DELETE CASCADE,
    FOREIGN KEY (doctor_id)  REFERENCES doctors(id)  ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS beds (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    bed_number VARCHAR(20) NOT NULL,
    status     VARCHAR(50) NOT NULL DEFAULT 'Available',
    created_at TIMESTAMP   DEFAULT CURRENT_TIMESTAMP
);

-- ----------------------------------------------------------
-- UNIVERSITY MODULE
-- ----------------------------------------------------------
CREATE TABLE IF NOT EXISTS students (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    course     VARCHAR(100) NOT NULL,
    year       INT          NOT NULL,
    created_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS faculty (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    name       VARCHAR(100) NOT NULL,
    department VARCHAR(100) NOT NULL,
    created_at TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS courses (
    id          INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL,
    credits     INT          NOT NULL,
    created_at  TIMESTAMP    DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS attendance (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT        NOT NULL,
    date       DATE       NOT NULL,
    status     VARCHAR(50) NOT NULL,
    created_at TIMESTAMP  DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS fees (
    id         INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT            NOT NULL,
    amount     DECIMAL(10, 2) NOT NULL,
    status     VARCHAR(50)    NOT NULL DEFAULT 'Unpaid',
    created_at TIMESTAMP      DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE
);
