CREATE TABLE operador (
    id_operador SERIAL PRIMARY KEY,
    nome VARCHAR(100),
    email VARCHAR(255),
    matricula VARCHAR(20),
    senha VARCHAR(20)
);


CREATE TABLE maquina(
	id_maquina SERIAL primary KEY,
	nome VARCHAR(30), 
	fabricante VARCHAR(50), 
	modelo VARCHAR(20),
	capacidade_operacional INT,
	data_aquisicao TIMESTAMP
);


CREATE TABLE ordem_servico(
	id_ordem_servico SERIAL PRIMARY KEY,	
	data_inicio TIMESTAMP,
	data_fim TIMESTAMP,
	status CHAR,
	velocidade_minima double precision,
	velocidade_maxima double precision,
	rpm_minimo double precision,
	rpm_maximo double precision,
	id_maquina_pk INT REFERENCES maquina(id_maquina)
);

create table ordem_servico_operador(
	id_ordem_pk INT REFERENCES ordem_servico(id_ordem_servico),
	id_operador_pk INT REFERENCES operador(id_operador)
);

-- Inserir dados na tabela operador
INSERT INTO operador (nome, email, matricula, senha)
VALUES 
  ('Operador 1', 'operador1@email.com', 'mat01', '1234'),
  ('Operador 2', 'operador2@email.com', 'mat02', '4567'),
  ('Operador 3', 'operador3@email.com', 'mat03', '7890');

 
INSERT INTO maquina (nome, fabricante, modelo, capacidade_operacional, data_aquisicao)
VALUES ('Colhedora 3000', 'New banana', 'Colhedora', 100, '2023-11-11 08:00:00');


-- Inserir dados na tabela ordem_servico
INSERT INTO ordem_servico (data_inicio, velocidade_minima, velocidade_maxima, rpm_minimo, rpm_maximo, id_maquina_pk)
VALUES 
  ('2023-11-11 08:00:00', 10.5, 20.5, 1000.0, 2000.0, 1);

-- Inserir dados na tabela ordem_servico_operador
INSERT INTO ordem_servico_operador (id_ordem_pk, id_operador_pk)
VALUES 
	(1, 1),
	(1, 2);

