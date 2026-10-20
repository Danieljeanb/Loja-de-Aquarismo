-- 1. CRIAÇÃO DO BANCO DE DADOS PROFISSIONAL
CREATE DATABASE IF NOT EXISTS `aquarismo_pro` 
CHARACTER SET utf8mb4 
COLLATE utf8mb4_unicode_ci;

USE `aquarismo_pro`;

-- ========================================================
-- 2. TABELA DE USUÁRIOS (Clientes e Funcionários)
-- ========================================================
CREATE TABLE IF NOT EXISTS `usuarios` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `nome` VARCHAR(100) NOT NULL,
  `email` VARCHAR(120) NOT NULL UNIQUE,
  `senha_hash` VARCHAR(255) NOT NULL,
  `role` VARCHAR(20) NOT NULL DEFAULT 'client'
) ENGINE=InnoDB;

-- ========================================================
-- 3. TABELA DE PRODUTOS (Aquários, Equipamentos e Peixes)
-- ========================================================
CREATE TABLE IF NOT EXISTS `produtos` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `nome` VARCHAR(100) NOT NULL,
  `categoria` VARCHAR(50) NOT NULL, -- 'aquario', 'equipamento' ou 'peixe'
  `descricao` TEXT NOT NULL,
  `preco` DECIMAL(10, 2) NOT NULL,
  `imagem` VARCHAR(255) DEFAULT 'placeholder.jpg',
  `estoque` INT NOT NULL DEFAULT 0
) ENGINE=InnoDB;

-- ========================================================
-- 4. TABELA DE DICAS (Portal de Conhecimento / Guias)
-- ========================================================
CREATE TABLE IF NOT EXISTS `dicas` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `titulo` VARCHAR(100) NOT NULL,
  `subtitulo` VARCHAR(150) DEFAULT NULL,
  `conteudo` TEXT NOT NULL,
  `icone` VARCHAR(50) DEFAULT 'fa-lightbulb'
) ENGINE=InnoDB;

-- ========================================================
-- 5. TABELA DE PEDIDOS (Histórico Geral)
-- ========================================================
CREATE TABLE IF NOT EXISTS `pedidos` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `total` DECIMAL(10, 2) NOT NULL,
  `data_pedido` DATETIME NOT NULL DEFAULT CURRENT_TIMESTAMP,
  `user_id` INT NULL,
  CONSTRAINT `fk_pedido_usuario` 
    FOREIGN KEY (`user_id`) REFERENCES `usuarios` (`id`) 
    ON DELETE SET NULL
) ENGINE=InnoDB;

-- ========================================================
-- 6. TABELA DE ITENS DOS PEDIDOS (Relacionamento N para N)
-- ========================================================
CREATE TABLE IF NOT EXISTS `itens_pedido` (
  `id` INT AUTO_INCREMENT PRIMARY KEY,
  `pedido_id` INT NOT NULL,
  `produto_nome` VARCHAR(100) NOT NULL,
  `quantidade` INT NOT NULL,
  `preco_unitario` DECIMAL(10, 2) NOT NULL,
  CONSTRAINT `fk_itens_pedido` 
    FOREIGN KEY (`pedido_id`) REFERENCES `pedidos` (`id`) 
    ON DELETE CASCADE
) ENGINE=InnoDB;


-- ========================================================
-- 7. INSERÇÃO DE DADOS INICIAIS DE TESTE (POPULAR O BANCO)
-- ========================================================

ALTER TABLE produtos ADD COLUMN subcategoria VARCHAR(50) NOT NULL DEFAULT 'geral' AFTER categoria;

-- Inserindo o Funcionário/Gerente Padrão
-- Nota: A senha abaixo corresponde ao hash scrypt da senha 'admin123'
INSERT INTO `usuarios` (`nome`, `email`, `senha_hash`, `role`) VALUES
('Gerente Geral', 'admin@loja.com', 'scrypt:32768:8:1vYg6MvXfD6hf8a8461b6c8914620f5c1d6836928e1d2de4bb7a7dfce92c68e16bc8912c98a58f70231cfb56c4d79df365022e5772390a1204d80a1c90bc89456209b53e89bb', 'employee')
ON DUPLICATE KEY UPDATE `id`=`id`;

-- Inserindo os Peixes Ornamentais (Conforme sua lista aprimorada)
INSERT INTO `produtos` (`nome`, `categoria`, `descricao`, `preco`, `imagem`, `estoque`) VALUES
('Betta Halfmoon', 'peixe', 'Peixe extremamente colorido, exuberante e ideal para pequenos aquários ou iniciantes.', 25.90, 'placeholder.jpg', 15),
('Tetra Neon', 'peixe', 'Pequeno, brilhante e cardumíneo. Excelente para dar vida a aquários comunitários plantados.', 6.50, 'placeholder.jpg', 120),
('Guppy Premium', 'peixe', 'Fácil manutenção, dócil e com uma grande variedade de cores na cauda. Perfeito para reprodução.', 12.90, 'placeholder.jpg', 45),
('Acará Bandeira', 'peixe', 'Traz elegância, imponência e um comportamento calmo ao topo e meio do seu ecossistema.', 45.90, 'placeholder.jpg', 0), -- Cadastrado como esgotado para testar a tarja
('Disco Red Melon', 'peixe', 'Conhecido mundialmente como o rei dos aquários de água doce por sua cor vermelha viva.', 199.90, 'placeholder.jpg', 8);

-- Inserindo os Guias e Dicas Técnicas (Para o portal de conhecimento)
INSERT INTO `dicas` (`titulo`, `subtitulo`, `conteudo`, `icone`) VALUES
('Montagem do Aquário', 'Passo a passo inicial para o sucesso', 'Posicione o tanque em uma superfície nivelada e firme, longe da luz solar direta para evitar surtos de algas. Instale o substrato antes de encher com água condicionada.', 'fa-box'),
('Ciclagem Biológica', 'O processo mais importante do ecossistema', 'A ciclagem consiste em aguardar de 20 a 40 dias com o filtro ligado antes de inserir qualquer peixe. Isso cria as bactérias benéficas que eliminam a amônia tóxica da água.', 'fa-rotate'),
('Limpeza e Manutenção', 'Métodos seguros de higienização', 'Nunca use sabão ou produtos químicos. Limpe os vidros com esponjas magnéticas e faça trocas parciais de água (TPA) lavando as mídias do filtro apenas com a própria água retirada do aquário.', 'fa-broom'),
('Alimentação Saudável', 'Nutrição equilibrada por espécie', 'Alimente seus peixes de 1 a 2 vezes ao dia, fornecendo apenas a quantidade exata que eles consigam consumir em até 3 minutos. Restos de comida no fundo disparam os níveis de amônia.', 'fa-fish-fins');
