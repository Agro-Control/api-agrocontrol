CREATE TABLE Gestor (
    id SERIAL PRIMARY KEY,
    cpf VARCHAR(11),
    nome VARCHAR(60),
    telefone VARCHAR(14),
	status CHAR DEFAULT 'A',
    email VARCHAR(60),
    data_contratacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	gestor_criacao_id INT,
	unidade_id INT
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
    status CHAR DEFAULT 'A',
	data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    telefone_responsavel VARCHAR(11),
    email_responsavel VARCHAR(60),
    nome_responsavel VARCHAR(60),
    gestor_criacao_id INT
);

CREATE TABLE Unidade(
	id SERIAL PRIMARY KEY,
    nome VARCHAR(60),
    cnpj VARCHAR(14),
    cep VARCHAR(8),
    estado VARCHAR(20),
    cidade VARCHAR(40),
    bairro VARCHAR(40),
    logradouro VARCHAR(60),
    numero VARCHAR(20),
    complemento VARCHAR(60),
    status CHAR DEFAULT 'A',
	data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    empresa_id INT,
    gestor_criacao_id INT
);


CREATE TABLE Operador (
    id SERIAL PRIMARY KEY,
    nome VARCHAR(100),
    email VARCHAR(255),
    matricula VARCHAR(20),
	cpf VARCHAR(11),
	status CHAR DEFAULT 'A',
	turno VARCHAR(5),
	telefone VARCHAR(14),
	data_contratacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	gestor_id INT,
	unidade_id INT
);

CREATE TABLE Talhao(
	id SERIAL PRIMARY KEY,
	codigo VARCHAR(10),
	tamanho VARCHAR(5),
	status CHAR DEFAULT 'A',
	gestor_id INT,
	unidade_id INT
);


CREATE TABLE Maquina(
	id SERIAL primary KEY,
	nome VARCHAR(30), 
	fabricante VARCHAR(50), 
	modelo VARCHAR(20),
	status CHAR DEFAULT 'A',
	capacidade_operacional INT,
	data_aquisicao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	gestor_id INT,
	unidade_id INT
);


CREATE TABLE Ordem_Servico(
	id SERIAL PRIMARY KEY,
	data_criacao TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	data_inicio TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	data_fim TIMESTAMP DEFAULT NULL,
	status CHAR DEFAULT 'A',
	velocidade_minima double precision,
	velocidade_maxima double precision,
	rpm double precision,
	id_gestor INT,
	id_unidade INT,
	id_talhao INT,
	id_maquina INT
);

CREATE TABLE Ordem_Servico_Operador(
	id_ordem_servico INT,
	id_operador INT
);

ALTER TABLE Gestor
ADD CONSTRAINT fk_gestor_gestor_criacao_id FOREIGN KEY (gestor_criacao_id) REFERENCES Gestor(id),
ADD CONSTRAINT fk_gestor_unidade_id FOREIGN KEY (unidade_id) REFERENCES Unidade(id);

ALTER TABLE Empresa
ADD CONSTRAINT fk_empresa_gestor_criacao_id FOREIGN KEY (gestor_criacao_id) REFERENCES Gestor(id);

ALTER TABLE Unidade
ADD CONSTRAINT fk_unidade_empresa_id FOREIGN KEY (empresa_id) REFERENCES Empresa(id),
ADD CONSTRAINT fk_unidade_gestor_criacao_id FOREIGN KEY (gestor_criacao_id) REFERENCES Gestor(id);

ALTER TABLE Operador
ADD CONSTRAINT fk_operador_gestor_id FOREIGN KEY (gestor_id) REFERENCES Gestor(id),
ADD CONSTRAINT fk_operador_unidade_id FOREIGN KEY (unidade_id) REFERENCES Unidade(id);

ALTER TABLE Talhao
ADD CONSTRAINT fk_talhao_gestor_id FOREIGN KEY (gestor_id) REFERENCES Gestor(id),
ADD CONSTRAINT fk_talhao_unidade_id FOREIGN KEY (unidade_id) REFERENCES Unidade(id);

ALTER TABLE Maquina
ADD CONSTRAINT fk_maquina_gestor_id FOREIGN KEY (gestor_id) REFERENCES Gestor(id),
ADD CONSTRAINT fk_maquina_unidade_id FOREIGN KEY (unidade_id) REFERENCES Unidade(id);

ALTER TABLE Ordem_Servico
ADD CONSTRAINT fk_ordem_servico_gestor_id FOREIGN KEY (id_gestor) REFERENCES Gestor(id),
ADD CONSTRAINT fk_ordem_servico_unidade_id FOREIGN KEY (id_unidade) REFERENCES Unidade(id),
ADD CONSTRAINT fk_ordem_servico_talhao_id FOREIGN KEY (id_talhao) REFERENCES Talhao(id),
ADD CONSTRAINT fk_ordem_servico_maquina_id FOREIGN KEY (id_maquina) REFERENCES Maquina(id);

ALTER TABLE Ordem_Servico_Operador
ADD CONSTRAINT fk_ordem_servico_operador_ordem_id FOREIGN KEY (id_ordem_servico) REFERENCES Ordem_Servico(id),
ADD CONSTRAINT fk_ordem_servico_operador_id FOREIGN KEY (id_operador) REFERENCES Operador(id);

--	Inserindo dados basicos	--

-- Inserir um gestor
INSERT INTO Gestor (cpf, nome, telefone, status, email)
VALUES ('21024436047', 'Gestor 1', '999999999', 'A', 'gestor1@example.com');

-- Inserir uma empresa
INSERT INTO Empresa (nome, cnpj, telefone, cep, estado, cidade, bairro, logradouro, telefone_responsavel, email_responsavel, nome_responsavel, gestor_criacao_id)
VALUES ('Empresa Exemplo', '74363470000156', '41998989898', '82315150', 'PR', 'Curitiba', 'São Braz', 'Concriz', '41999999999', 'responsavel@example.com', 'Responsável', 1);

-- Inserir duas unidades
INSERT INTO Unidade (nome, cnpj, cep, estado, cidade, bairro, logradouro, status, empresa_id, gestor_criacao_id)
VALUES ('Unidade 1', '00213983000144', '81170230', 'PR', 'Curitiba', 'Cidade Indutrial', 'Cyro Correia Pereira','A', 1, 1),
       ('Unidade 2', '08292207000199', '81590510', 'PR', 'Curitiba', 'Uberaba', 'Olindo Caetani', 'A', 1, 1);

-- Inserir dois operadores
INSERT INTO Operador (cpf, nome, turno, email, gestor_id, unidade_id)
VALUES ('01590575075', 'Operador 1', 'Manhã', 'operador1@example.com', 1, 1),
       ('37915129007', 'Operador 2', 'Tarde', 'operador2@example.com', 1, 2);

-- Inserir uma máquina
INSERT INTO Maquina (nome, fabricante, modelo, capacidade_operacional, gestor_id, unidade_id)
VALUES ('Máquina 1', 'Fabricante 1', 'Modelo 1', 100, 1, 1);

-- Inserir um talhão
INSERT INTO Talhao (codigo, tamanho, status, gestor_id, unidade_id)
VALUES ('1234', '10', 'A', 1, 1);

-- Inserir uma ordem de serviço
INSERT INTO Ordem_Servico (velocidade_minima, velocidade_maxima, rpm, id_gestor, id_unidade, id_talhao, id_maquina)
VALUES (10.5, 20.5, 1000.0, 1, 1, 1, 1);

-- Inserir um talhão
INSERT INTO Ordem_Servico_Operador (id_ordem_servico, id_operador) 
VALUES	(1, 1);

