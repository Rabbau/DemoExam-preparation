-- Структура БД системы оформления заказов обуви (3НФ).
-- Запуск: psql -U postgres -d shoe_shop -f database/create_db.sql

SET client_encoding = 'UTF8';

DROP TABLE IF EXISTS order_item CASCADE;
DROP TABLE IF EXISTS customer_order CASCADE;
DROP TABLE IF EXISTS product_size CASCADE;
DROP TABLE IF EXISTS shoe_size CASCADE;
DROP TABLE IF EXISTS product CASCADE;
DROP TABLE IF EXISTS manufacturer CASCADE;
DROP TABLE IF EXISTS category CASCADE;
DROP TABLE IF EXISTS app_user CASCADE;
DROP TABLE IF EXISTS role CASCADE;

CREATE TABLE role (
    role_id   SERIAL PRIMARY KEY,
    role_name VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE app_user (
    user_id    SERIAL PRIMARY KEY,
    role_id    INT NOT NULL REFERENCES role (role_id) ON DELETE RESTRICT,
    last_name  VARCHAR(100) NOT NULL,
    first_name VARCHAR(100) NOT NULL,
    patronymic VARCHAR(100),
    login      VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE category (
    category_id   SERIAL PRIMARY KEY,
    category_name VARCHAR(100) NOT NULL UNIQUE
);

CREATE TABLE manufacturer (
    manufacturer_id   SERIAL PRIMARY KEY,
    manufacturer_name VARCHAR(150) NOT NULL UNIQUE
);

-- Модель обуви. Остатки хранятся не здесь, а по каждому размеру в product_size.
CREATE TABLE product (
    product_id      SERIAL PRIMARY KEY,
    article         VARCHAR(20) NOT NULL UNIQUE,
    product_name    VARCHAR(200) NOT NULL,
    category_id     INT NOT NULL REFERENCES category (category_id) ON DELETE RESTRICT,
    manufacturer_id INT NOT NULL REFERENCES manufacturer (manufacturer_id) ON DELETE RESTRICT,
    price           NUMERIC(10, 2) NOT NULL CHECK (price >= 0),
    composition     VARCHAR(300),
    description     TEXT,
    photo           VARCHAR(255)
);

CREATE TABLE shoe_size (
    size_id    SERIAL PRIMARY KEY,
    size_value NUMERIC(3, 1) NOT NULL UNIQUE CHECK (size_value > 0)
);

-- Товарная позиция: сочетание модели и размера с доступным количеством.
-- Все строки модели (в т.ч. с нулевым остатком) образуют её размерный ряд.
CREATE TABLE product_size (
    product_size_id SERIAL PRIMARY KEY,
    product_id      INT NOT NULL REFERENCES product (product_id) ON DELETE CASCADE,
    size_id         INT NOT NULL REFERENCES shoe_size (size_id) ON DELETE RESTRICT,
    quantity        INT NOT NULL DEFAULT 0 CHECK (quantity >= 0),
    UNIQUE (product_id, size_id)
);

CREATE TABLE customer_order (
    order_id   SERIAL PRIMARY KEY,
    user_id    INT NOT NULL REFERENCES app_user (user_id) ON DELETE RESTRICT,
    order_date DATE NOT NULL DEFAULT CURRENT_DATE
);

-- unit_price фиксирует цену со скидкой на момент заказа: каталожная цена может измениться позже.
CREATE TABLE order_item (
    order_item_id   SERIAL PRIMARY KEY,
    order_id        INT NOT NULL REFERENCES customer_order (order_id) ON DELETE CASCADE,
    product_size_id INT NOT NULL REFERENCES product_size (product_size_id) ON DELETE RESTRICT,
    quantity        INT NOT NULL CHECK (quantity > 0),
    unit_price      NUMERIC(10, 2) NOT NULL CHECK (unit_price >= 0),
    UNIQUE (order_id, product_size_id)
);

CREATE INDEX idx_customer_order_date ON customer_order (order_date);
