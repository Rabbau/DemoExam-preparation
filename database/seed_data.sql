-- Тестовые данные для тренировки. На экзамене вместо них загружаются файлы заказчика.
-- Даты заказов считаются от CURRENT_DATE, чтобы скидка 25% всегда была видна на части товаров.

-- Без этого psql в Windows читает файл как WIN1251 и падает на кириллице.
SET client_encoding = 'UTF8';

INSERT INTO role (role_id, role_name) VALUES
    (1, 'Администратор'),
    (2, 'Менеджер'),
    (3, 'Авторизированный клиент');

INSERT INTO app_user (user_id, role_id, last_name, first_name, patronymic, login) VALUES
    (1, 1, 'Никитина', 'Светлана', 'Олеговна', 'admin'),
    (2, 2, 'Орлов', 'Денис', 'Игоревич', 'manager'),
    (3, 3, 'Ковалёва', 'Анна', 'Сергеевна', 'client1'),
    (4, 3, 'Петров', 'Максим', 'Андреевич', 'client2'),
    (5, 3, 'Широкова', 'Елена', NULL, 'client3');

INSERT INTO category (category_id, category_name) VALUES
    (1, 'Кроссовки'),
    (2, 'Ботинки'),
    (3, 'Туфли'),
    (4, 'Сапоги'),
    (5, 'Кеды');

INSERT INTO manufacturer (manufacturer_id, manufacturer_name) VALUES
    (1, 'Фабрика «Заря»'),
    (2, 'Обувь Урала'),
    (3, 'СтепЛайн'),
    (4, 'Comfort Walk');

INSERT INTO product (product_id, article, product_name, category_id, manufacturer_id, price, composition, description, photo) VALUES
    (1, 'SH-001', 'Кроссовки беговые «Спринт»', 1, 3, 5490.00, 'Верх: текстиль; подошва: ЭВА', 'Лёгкие кроссовки для бега по асфальту, амортизирующая пятка.', 'sh001.png'),
    (2, 'SH-002', 'Кроссовки городские «Метро»', 1, 4, 4290.00, 'Верх: искусственная кожа; подошва: резина', 'Повседневная модель на каждый день.', 'sh002.png'),
    (3, 'SH-003', 'Ботинки зимние «Тайга»', 2, 2, 8990.00, 'Верх: натуральная кожа; подкладка: шерсть', 'Тёплые ботинки до −30 °C, нескользящая подошва.', 'sh003.png'),
    (4, 'SH-004', 'Ботинки демисезонные «Норд»', 2, 1, 6790.00, 'Верх: замша; подошва: ТЭП', 'Классические ботинки на шнуровке.', NULL),
    (5, 'SH-005', 'Туфли классические «Бизнес»', 3, 1, 5990.00, 'Верх: натуральная кожа; подошва: кожа', 'Мужские туфли для офиса.', NULL),
    (6, 'SH-006', 'Туфли-лодочки «Грация»', 3, 4, 4790.00, 'Верх: лакированная кожа', 'Женские туфли на устойчивом каблуке 6 см.', 'missing_photo.png'),
    (7, 'SH-007', 'Сапоги женские «Вьюга»', 4, 2, 10490.00, 'Верх: натуральная кожа; подкладка: мех', 'Высокие сапоги на молнии.', NULL),
    (8, 'SH-008', 'Кеды «Старт»', 5, 3, 2490.00, 'Верх: хлопок; подошва: резина', 'Классические кеды, подходят для спорта и прогулок.', NULL),
    (9, 'SH-009', 'Кеды высокие «Скейт»', 5, 4, 3190.00, 'Верх: текстиль; подошва: резина', 'Высокие кеды с усиленным носком.', NULL),
    (10, 'SH-010', 'Сапоги резиновые «Дождь»', 4, 1, 1990.00, 'ПВХ', 'Непромокаемые сапоги для дачи и прогулок.', NULL);

INSERT INTO shoe_size (size_value) VALUES
    (36), (37), (38), (39), (40), (41), (42), (43), (44), (45);

-- Остатки подобраны так, чтобы были все случаи: «много» (> 5), «мало» (4–5), подсветка (≤ 3), ноль.
INSERT INTO product_size (product_id, size_id, quantity)
SELECT v.product_id, s.size_id, v.quantity
FROM (VALUES
    (1, 40, 4), (1, 41, 3), (1, 42, 5), (1, 43, 0),
    (2, 39, 1), (2, 40, 2), (2, 41, 0),
    (3, 41, 2), (3, 42, 3), (3, 43, 2), (3, 44, 1),
    (4, 40, 1), (4, 42, 1), (4, 44, 0),
    (5, 41, 3), (5, 42, 2),
    (6, 36, 2), (6, 37, 4), (6, 38, 3), (6, 39, 1),
    (7, 36, 0), (7, 37, 1), (7, 38, 1),
    (8, 37, 6), (8, 38, 5), (8, 39, 4), (8, 40, 7),
    (9, 38, 0), (9, 39, 0), (9, 40, 0),
    (10, 36, 5), (10, 38, 5), (10, 40, 5), (10, 42, 5)
) AS v (product_id, size_value, quantity)
JOIN shoe_size s ON s.size_value = v.size_value;

INSERT INTO customer_order (order_id, user_id, order_date) VALUES
    (1, 3, (date_trunc('month', CURRENT_DATE) - INTERVAL '20 days')::date),
    (2, 4, (date_trunc('month', CURRENT_DATE) - INTERVAL '5 days')::date),
    (3, 3, CURRENT_DATE),
    (4, 5, (date_trunc('month', CURRENT_DATE) - INTERVAL '45 days')::date);

-- Заказы прошлого месяца есть у моделей 1, 2, 3, 8 — на них скидки нет.
INSERT INTO order_item (order_id, product_size_id, quantity, unit_price)
SELECT v.order_id, ps.product_size_id, v.quantity, v.unit_price
FROM (VALUES
    (1, 1, 41, 1, 4117.50),
    (1, 2, 40, 2, 3217.50),
    (2, 3, 42, 1, 6742.50),
    (2, 8, 38, 2, 1867.50),
    (3, 4, 42, 1, 6790.00),
    (4, 5, 41, 1, 5990.00)
) AS v (order_id, product_id, size_value, quantity, unit_price)
JOIN shoe_size s ON s.size_value = v.size_value
JOIN product_size ps ON ps.product_id = v.product_id AND ps.size_id = s.size_id;

-- Явные id сбили счётчики SERIAL: выставляем их на максимум, иначе следующий INSERT упадёт.
SELECT setval(pg_get_serial_sequence('role', 'role_id'), (SELECT MAX(role_id) FROM role));
SELECT setval(pg_get_serial_sequence('app_user', 'user_id'), (SELECT MAX(user_id) FROM app_user));
SELECT setval(pg_get_serial_sequence('category', 'category_id'), (SELECT MAX(category_id) FROM category));
SELECT setval(pg_get_serial_sequence('manufacturer', 'manufacturer_id'), (SELECT MAX(manufacturer_id) FROM manufacturer));
SELECT setval(pg_get_serial_sequence('product', 'product_id'), (SELECT MAX(product_id) FROM product));
SELECT setval(pg_get_serial_sequence('customer_order', 'order_id'), (SELECT MAX(order_id) FROM customer_order));
