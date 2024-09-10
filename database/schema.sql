CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) NOT NULL,
    password VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL,
    role ENUM('customer', 'shop_owner') NOT NULL
);

CREATE TABLE shops (
    id INT AUTO_INCREMENT PRIMARY KEY,
    owner_id INT,
    name VARCHAR(255) NOT NULL,
    address VARCHAR(255) NOT NULL,
    phone VARCHAR(20),
    FOREIGN KEY (owner_id) REFERENCES users(id)
);

CREATE TABLE appointments (
    id INT AUTO_INCREMENT PRIMARY KEY,
    customer_id INT,
    shop_id INT,
    appointment_date DATETIME NOT NULL,
    status ENUM('pending', 'confirmed', 'canceled') NOT NULL,
    FOREIGN KEY (customer_id) REFERENCES users(id),
    FOREIGN KEY (shop_id) REFERENCES shops(id)
);
