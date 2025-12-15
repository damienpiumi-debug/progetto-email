CREATE TABLE IF NOT EXISTS spedizioni (
    id INT AUTO_INCREMENT PRIMARY KEY,
    letter_id VARCHAR(255),
    destinatario VARCHAR(255),
    indirizzo VARCHAR(255),
    stato VARCHAR(100)
);
