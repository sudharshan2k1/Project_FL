"""create database phonepe_splitwise;
use phonepe_splitwise;  -- group --> split_group
CREATE TABLE users (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    mobile VARCHAR(10) UNIQUE,
    password VARCHAR(255),
    role ENUM('admin','user') DEFAULT 'user'
);
CREATE TABLE split_group (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(50),
    created_by INT,
    FOREIGN KEY (created_by) REFERENCES users(id)
);
CREATE TABLE group_members (
    group_id INT,
    user_id INT,
    PRIMARY KEY (group_id, user_id),
    FOREIGN KEY (group_id) REFERENCES split_group(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE TABLE expenses (
    id INT AUTO_INCREMENT PRIMARY KEY,
    group_id INT,
    description VARCHAR(100),
    total_amount DECIMAL(10,2),
    paid_by INT,
    FOREIGN KEY (group_id) REFERENCES split_group(id),
    FOREIGN KEY (paid_by) REFERENCES users(id)
);
CREATE TABLE expense_splits (
    expense_id INT,
    user_id INT,
    share_amount DECIMAL(10,2),
    paid_amount DECIMAL(10,2),
    balance DECIMAL(10,2),
    FOREIGN KEY (expense_id) REFERENCES expenses(id),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
select * from users;
select * from split_group;
select * from group_members;
select * from expenses;
select * from expense_splits;"""