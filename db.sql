-- CRIANDO A BASE DE DADOS
CREATE DATABASE IF NOT EXISTS crisma;
USE crisma;


-- UM crismando pode ter apenas UM catequista (1:1)


-- CRIANDO AS TABELAS NECESSÁRIAS
CREATE TABLE IF NOT EXISTS catequistas (
	id_catequista INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    data_nascimento DATE NOT NULL,
    grupo VARCHAR(100) DEFAULT "Nao Especificado",
    nivel ENUM('coordenador', 'catequista') DEFAULT 'catequista',
    status_informacao BOOLEAN DEFAULT 1
);

-- ALTER TABLE catequistas
-- ADD COLUMN status_informacao BOOLEAN DEFAULT 1;


CREATE TABLE IF NOT EXISTS crismandos (
	id INT PRIMARY KEY AUTO_INCREMENT,
    nome VARCHAR(100) NOT NULL,
    nome_mae VARCHAR(100) NOT NULL,
    nome_pai VARCHAR(100) DEFAULT 'Não mencionado',
    data_nascimento DATE NOT NULL,
    endereco VARCHAR(200) NOT NULL,
    cidade VARCHAR(100),
    tel1 VARCHAR(20) NOT NULL,
    tel2 VARCHAR(20),
    batismo ENUM('sim', 'nao') DEFAULT 'nao',
    eucaristia ENUM('sim', 'nao') DEFAULT 'nao',
    status_crismando ENUM('ativo', 'desistente') DEFAULT 'ativo',
    fk_id_catequista INT,
    
    CONSTRAINT fk_catequista_crismando
    FOREIGN KEY (fk_id_catequista) REFERENCES catequistas(id_catequista)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);

-- UM crismando pode ter VARIAS frequencias (1:N)


-- ALTER TABLE crismandos
-- CHANGE tel1 tel1 VARCHAR(20);

-- ALTER TABLE crismandos
-- CHANGE tel2 tel2 VARCHAR(20);



CREATE TABLE IF NOT EXISTS infor_frequencias (
	id_infor_freq INT PRIMARY KEY AUTO_INCREMENT,
    titulo_encontro VARCHAR(250) NOT NULL,
    data_chamada DATE NOT NULL,
    fk_id_freq INT NOT NULL
);

CREATE TABLE IF NOT EXISTS frequencias (
    id_freq INT PRIMARY KEY AUTO_INCREMENT,
    fk_id_crismando INT NOT NULL,
    fk_id_infor_freq INT,
    status_frequencia ENUM('presente', 'falta', 'justificada') DEFAULT 'presente',
    observacao TEXT NULL,

    CONSTRAINT fk_crismando_frequencia
    FOREIGN KEY (fk_id_crismando) REFERENCES crismandos(id)
    ON DELETE CASCADE
    ON UPDATE CASCADE,
    
    CONSTRAINT fk_frequencia_inforfrequencia
    FOREIGN KEY (fk_id_infor_freq) REFERENCES infor_frequencias(id_infor_freq)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);


ALTER TABLE infor_frequencias
ADD CONSTRAINT fk_infor_freq_freq
FOREIGN KEY (fk_id_freq) REFERENCES frequencias(id_freq)
ON DELETE CASCADE
ON UPDATE CASCADE;

-- ALTER TABLE frequencias
-- RENAME COLUMN status TO status_frequencia;


CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario INT PRIMARY KEY AUTO_INCREMENT,
    email VARCHAR(100) UNIQUE NOT NULL,
    senha_hash VARCHAR(255) NOT NULL,
    fk_id_catequista INT UNIQUE NOT NULL,

    CONSTRAINT fk_usuario_catequista
    FOREIGN KEY (fk_id_catequista) REFERENCES catequistas(id_catequista)
    ON DELETE CASCADE
    ON UPDATE CASCADE
);


-- ALGUNS INSERT's para servir só de exemplos
INSERT INTO catequistas (nome, data_nascimento, grupo, nivel)
VALUES 
('João da Silva', '1985-06-15', 'Grupo A', 'catequista'),
('Maria Oliveira', '1978-11-22', 'Grupo B', 'coordenador');


INSERT INTO crismandos (nome, nome_mae, nome_pai, data_nascimento, endereco, tel1, tel2, batismo, eucaristia, status_crismando, fk_id_catequista)
VALUES 
('Lucas Pereira', 'Ana Pereira', 'Carlos Pereira', '2005-04-10', 'Rua das Flores, 123', '999999999', '988888888', 'sim', 'sim', 'ativo', 1),
('Fernanda Souza', 'Cláudia Souza', 'Roberto Souza', '2006-08-25', 'Avenida Central, 456', '977777777', NULL, 'sim', 'nao', 'ativo', 2),
('Pedro Lima', 'Juliana Lima', 'Não mencionado', '2004-12-15', 'Rua do Sol, 789', '966666666', '955555555', 'nao', 'sim', 'desistente', 1);


INSERT INTO frequencias (fk_id_crismando, data_frequencia, status_frequencia, observacao)
VALUES 
(1, '2025-03-01', 'presente', 'Chegou cedo, participou ativamente'),
(2, '2025-03-01', 'justificada', 'Faltou devido a viagem com a família'),
(3, '2025-03-01', 'falta', 'Não compareceu à catequese'),
(1, '2025-03-08', 'presente', 'Participou de todas as atividades');


-- TESTANDO UMAS COISAS


SELECT * FROM catequistas;
SELECT * FROM crismandos;
SELECT * FROM frequencias;

SELECT
	c.id,
	c.nome,
    COUNT(f.status_frequencia) AS quant_frequencia
FROM frequencias f
INNER JOIN crismandos c ON f.fk_id_crismando = c.id
WHERE status_frequencia = 'presente'
GROUP BY c.id, c.nome;