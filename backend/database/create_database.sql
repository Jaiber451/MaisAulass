DROP DATABASE IF EXISTS mais_aulas;
CREATE DATABASE mais_aulas CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci;
USE mais_aulas;

CREATE TABLE usuario (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  nome VARCHAR(100) NOT NULL,
  email VARCHAR(100) NOT NULL UNIQUE,
  senha_hash VARCHAR(512)
);

CREATE TABLE sessao (
  sessao_id INT AUTO_INCREMENT PRIMARY KEY,
  token_hash VARCHAR(64) NOT NULL UNIQUE,
  user_id INT NOT NULL,
  CONSTRAINT fk_sessao_usuario FOREIGN KEY (user_id) REFERENCES usuario(user_id) ON DELETE CASCADE
);

CREATE TABLE turma (
  turma_id INT AUTO_INCREMENT PRIMARY KEY,
  nome_turma VARCHAR(100) NOT NULL,
  user_id INT NOT NULL,
  descricao_atividade VARCHAR(100),
  CONSTRAINT fk_turma_usuario FOREIGN KEY (user_id) REFERENCES usuario(user_id) ON DELETE CASCADE
);

CREATE TABLE atividade (
  atividade_id INT AUTO_INCREMENT PRIMARY KEY,
  titulo VARCHAR(100) NOT NULL,
  descricao_atividade VARCHAR(100),
  turma_id INT NOT NULL,
  data_entrega VARCHAR(100) NOT NULL,
  CONSTRAINT fk_atividade_turma FOREIGN KEY (turma_id) REFERENCES turma(turma_id) ON DELETE CASCADE
);

CREATE TABLE entrega (
  entrega_id INT AUTO_INCREMENT PRIMARY KEY,
  data_entrega VARCHAR(100) NOT NULL,
  status_entrega VARCHAR(100) NOT NULL,
  atividade_id INT NOT NULL,
  user_id INT NOT NULL,
  nota INT,
  CONSTRAINT fk_entrega_atividade FOREIGN KEY (atividade_id) REFERENCES atividade(atividade_id) ON DELETE CASCADE,
  CONSTRAINT fk_entrega_usuario FOREIGN KEY (user_id) REFERENCES usuario(user_id) ON DELETE CASCADE
);
