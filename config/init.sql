CREATE TABLE Usuario (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100),
    cpf VARCHAR(11),
    telefone VARCHAR(14),
    turno CHAR,
    email VARCHAR(255),
    matricula VARCHAR(20),
    senha VARCHAR(255),
    data_contratacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    tipo CHAR(1),
    status CHAR DEFAULT 'A',  --COMMENT 'TABELA STATUS: A = ATIVO, I = INATIVO',
    gestor_id INT,
    empresa_id INT,
    unidade_id INT,
    grupo_id INT
);

CREATE TABLE Grupo (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100),
    status CHAR DEFAULT 'A',  --COMMENT 'TABELA STATUS: A = ATIVO, I = INATIVO',
    data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE Empresa (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(60),
    cnpj VARCHAR(14),
    telefone VARCHAR(11),
    cep VARCHAR(8),
    estado VARCHAR(20),
    cidade VARCHAR(40),
    bairro VARCHAR(40),
    logradouro VARCHAR(60),
    numero VARCHAR(20),
    complemento VARCHAR(60),
    status CHAR DEFAULT 'A',  --COMMENT 'TABELA STATUS: A = ATIVO, I = INATIVO',
	data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    grupo_id INT
);

CREATE TABLE Unidade(
	id SERIAL PRIMARY KEY,
    nome VARCHAR(60),
    cep VARCHAR(8),
    estado VARCHAR(20),
    cidade VARCHAR(40),
    bairro VARCHAR(40),
    logradouro VARCHAR(60),
    numero VARCHAR(20),
    complemento VARCHAR(60),
    status CHAR DEFAULT 'A',  --COMMENT 'TABELA STATUS: A = ATIVO, I = INATIVO',
	data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    empresa_id INT,
    gestor_id INT
);

CREATE TABLE Talhao(
	id SERIAL PRIMARY KEY,
	codigo VARCHAR(10),
	tamanho VARCHAR(5),
	status CHAR DEFAULT 'A',  --COMMENT 'TABELA STATUS: A = ATIVO, I = INATIVO',
	unidade_id INT
);

CREATE TABLE Maquina(
	id SERIAL primary KEY,
	nome VARCHAR(30), 
	fabricante VARCHAR(50), 
	modelo VARCHAR(20),
	status CHAR DEFAULT 'A',  --COMMENT 'TABELA STATUS: A = ATIVO, I = INATIVO, M = MANUTENCAO',
	capacidade_operacional INT,
	data_aquisicao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	unidade_id INT

);

CREATE TABLE Ordem_Servico(
	id SERIAL PRIMARY KEY,
	data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	data_inicio TIMESTAMP DEFAULT NULL,
	data_previsao_fim TIMESTAMP  DEFAULT NULL,
	data_fim TIMESTAMP DEFAULT NULL,
	status CHAR DEFAULT 'A',  --COMMENT 'TABELA STATUS: A = ATIVO, E = EXECUTANDO, F = FINALIZADO, C = CANCELADO',
	velocidade_minima double precision,
	velocidade_maxima double precision,
	rpm double precision,
	gestor_id INT,
	unidade_id INT,
	empresa_id INT,
	talhao_id INT,
	maquina_id INT
);

CREATE TABLE Ordem_Servico_Operador(
	ordem_servico_id INT,
	operador_id INT
);

ALTER TABLE Usuario
ADD CONSTRAINT fk_usuario_gestor_criacao_id FOREIGN KEY (gestor_id) REFERENCES Usuario(id),
ADD CONSTRAINT fk_usuario_empresa_id FOREIGN KEY (empresa_id) REFERENCES Empresa(id),
ADD CONSTRAINT fk_usuario_unidade_id FOREIGN KEY (unidade_id) REFERENCES Unidade(id),
ADD CONSTRAINT fk_usuario_grupo_id FOREIGN KEY (grupo_id) REFERENCES Grupo(id);

ALTER TABLE Empresa
ADD CONSTRAINT fk_empresa_grupo_id FOREIGN KEY (grupo_id) REFERENCES Grupo(id);

ALTER TABLE Unidade
ADD CONSTRAINT fk_unidade_empresa_id FOREIGN KEY (empresa_id) REFERENCES Empresa(id),
ADD CONSTRAINT fk_unidade_gestor_criacao_id FOREIGN KEY (gestor_id) REFERENCES Usuario(id);

ALTER TABLE Talhao
ADD CONSTRAINT fk_talhao_unidade_id FOREIGN KEY (unidade_id) REFERENCES Unidade(id);

ALTER TABLE Maquina
ADD CONSTRAINT fk_maquina_unidade_id FOREIGN KEY (unidade_id) REFERENCES Unidade(id);

ALTER TABLE Ordem_Servico
ADD CONSTRAINT fk_ordem_servico_gestor_id FOREIGN KEY (gestor_id) REFERENCES Usuario(id),
ADD CONSTRAINT fk_ordem_servico_unidade_id FOREIGN KEY (unidade_id) REFERENCES Unidade(id),
ADD CONSTRAINT fk_ordem_servico_empresa_id FOREIGN KEY (empresa_id) REFERENCES Empresa(id),
ADD CONSTRAINT fk_ordem_servico_talhao_id FOREIGN KEY (talhao_id) REFERENCES Talhao(id),
ADD CONSTRAINT fk_ordem_servico_maquina_id FOREIGN KEY (maquina_id) REFERENCES Maquina(id);

ALTER TABLE Ordem_Servico_Operador
ADD CONSTRAINT fk_ordem_servico_operador_ordem_id FOREIGN KEY (ordem_servico_id) REFERENCES Ordem_Servico(id),
ADD CONSTRAINT fk_ordem_servico_operador_id FOREIGN KEY (operador_id) REFERENCES Usuario(id);


-- Inserir um admin pela saco (versão final é o unico gp que deve existir)
INSERT INTO Grupo (nome)
VALUES ('Prime Group'), ('Second Group');

-- Inserir um admin pela saco (versão final é o unico cara que deve existir)
INSERT INTO Usuario (nome, email, tipo, senha, grupo_id)
VALUES ('Diretor 1', 'diretor1@gmail.com', 'D', '$2b$12$X48WhMbJSsKZMmIC2YUHieKpDC6WAC5Y2Y5BIVhQ6bPNpzZtjuCSO', 1),
        ('Diretor 2', 'diretor2@gmail.com', 'D', '$2b$12$X48WhMbJSsKZMmIC2YUHieKpDC6WAC5Y2Y5BIVhQ6bPNpzZtjuCSO', 2);

-- Inserir uma empresa
INSERT INTO Empresa (nome, cnpj, telefone, cep, estado, cidade, bairro, logradouro, grupo_id)
VALUES ('Empresa1', '74363470000156', '41998989898', '82315150', 'PR', 'Curitiba', 'São Braz', 'Concriz', 1),
        ('Empresa2', '74363470000156', '41998989898', '82315150', 'PR', 'Curitiba', 'São Braz', 'Concriz', 2);

-- Inserir um gestor
INSERT INTO Usuario (cpf, nome, telefone, email, tipo, grupo_id, empresa_id, senha)
VALUES ('21024436047', 'Gestor 1', '999999999', 'gestor1@example.com', 'G', 1, 1, '$2b$12$vOZ5S37hIDGN2Qz/w.XVq.qFdr8jkPqF/NEkLz2dWey7EawMhdfOa');

-- Inserir duas unidades
INSERT INTO Unidade (nome, cep, estado, cidade, bairro, logradouro, empresa_id, gestor_id)
VALUES ('Unidade 1', '81170230', 'PR', 'Curitiba', 'Cidade Industrial', 'Cyro Correia Pereira', 1, 1),
       ('Unidade 2', '81590510', 'PR', 'Curitiba', 'Uberaba', 'Olindo Caetani', 1, 1);

-- Inserir operadores
INSERT INTO Usuario (cpf, matricula, nome, turno, gestor_id, grupo_id, empresa_id, unidade_id, tipo, email, senha)
VALUES ('01590575075', '202400001', 'Vinicius', 'M', 1, 1, 1, 1, 'O', 'vinicius@example.com', '$2b$12$MSOV1vVhuTCmf0lTIkNNjuhVtxZ7xXV.DGIiq5NrRO2.HXCOS.aWW'),
       ('01590575076', '202400002', 'Maicon', 'T', 1, 1, 1, 1, 'O', 'maicon@example.com', '$2b$12$DPiNCoqQ3AVviY3vSU7QyemeGXZUDgkF7NiHlWbYFX61zaVMQfB/G'),
       ('38135804075', '202400003', 'Cristopher', 'N', 1, 1, 1, 1, 'O', 'critopher@example.com', '$2b$12$C8ksPA7N.1twxZoqUpyRsefeQ14LauYieX.nunTY0p6s3qHVcXt/O'),
       ('73941491024', '202400004', 'Gabriel', 'N', 1, 1, 1, 2, 'O', 'gabriel@example.com', '$2b$12$yRbKsqv9t1WJ6xfqnU9niOv.csKHqMS8.T8AywJG40R631BI4CGni');

-- Inserir uma máquina
INSERT INTO Maquina (nome, fabricante, modelo, capacidade_operacional, unidade_id)
VALUES ('Máquina 1', 'Fabricante 1', 'Modelo 1', 100, 1),
       ('Máquina 2', 'Fabricante 2', 'Modelo 2', 90, 1);

-- Inserir um talhão
INSERT INTO Talhao (codigo, tamanho, status, unidade_id)
VALUES ('1234', '10', 'A', 1);

