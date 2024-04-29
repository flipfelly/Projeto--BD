CREATE VIEW VendasMensais AS
SELECT 
    DATE_FORMAT(v.data_venda, '%Y-%m') AS Mes,
    f.nome AS Vendedor,
    SUM(v.valor) AS Total_Vendas
FROM Venda v
JOIN Funcionario f ON v.funcionario_id = f.id
GROUP BY DATE_FORMAT(v.data_venda, '%Y-%m'), f.nome;
DELIMITER //

CREATE PROCEDURE GerarRelatorioMensal(IN mes_ano VARCHAR(7))
BEGIN
    SELECT * FROM VendasMensais WHERE Mes = mes_ano;
END //

DELIMITER ;
CREATE INDEX idx_funcionario_id ON Venda (funcionario_id);
ALTER TABLE Venda ADD CONSTRAINT fk_funcionario_venda
FOREIGN KEY (funcionario_id)
REFERENCES Funcionario(id);

ALTER TABLE Venda ADD CONSTRAINT fk_livro_venda
FOREIGN KEY (livro_id)
REFERENCES Livro(id);

ALTER TABLE Livro ADD CONSTRAINT fk_autor_livro
FOREIGN KEY (autor_id)
REFERENCES Autor(id);

ALTER TABLE Livro ADD CONSTRAINT fk_editora_livro
FOREIGN KEY (editora_id)
REFERENCES Editora(id);

ALTER TABLE Livro ADD CONSTRAINT fk_genero_livro
FOREIGN KEY (genero_id)
REFERENCES Genero(id);

ALTER TABLE Cliente ADD CONSTRAINT fk_user_cliente
FOREIGN KEY (user_id)
REFERENCES User(id);

ALTER TABLE Funcionario ADD CONSTRAINT fk_user_funcionario
FOREIGN KEY (user_id)
REFERENCES User(id);