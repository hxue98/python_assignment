-- Create DB if not exist
CREATE DATABASE IF NOT EXISTS stocks;

-- Select stocks as DB
USE stocks;

-- Create Tables
CREATE TABLE IF NOT EXISTS financial_data(
    `symbol`        VARCHAR(20),
    `date`          DATE,
    `open_price`    DECIMAL(20, 2),
    `close_price`   DECIMAL(20, 2),
    `volume`        BIGINT,

    -- Constraints
    PRIMARY KEY(`symbol`, `date`)
);