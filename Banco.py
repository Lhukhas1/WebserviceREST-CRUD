import sqlite3

class Banco:
    def __init__(self):
        self.conexao = sqlite3.connect("teste.db", check_same_thread=False)
        cursor = self.conexao.cursor()
        cursor.execute("CREATE TABLE IF NOT EXISTS Materias(codigo PRIMARY KEY, nomeDisciplina, nomeProfessor, quantidadeAlunos, cargaHoraria, mediaTurma)")

        # Nova Tabela para Alunos, linkando Alunos com Materias via codigoDisciplina
        cursor.execute("""CREATE TABLE IF NOT EXISTS Alunos(
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            nome, 
            codigoDisciplina, 
            nota,
            FOREIGN KEY(codigoDisciplina) REFERENCES Materias(codigo)
        )""")
        self.conexao.commit()
        cursor.close()
    
    # Metodos para Materias
    def adicionar(self, codigo, nomeDisciplina, nomeProfessor, quantidadeAlunos, cargaHoraria, mediaTurma):
        cursor = self.conexao.cursor()
        cursor.execute(
            "INSERT INTO Materias(codigo, nomeDisciplina, nomeProfessor, quantidadeAlunos, cargaHoraria, mediaTurma) VALUES(?, ?, ?, ?, ?, ?)",
            (codigo, nomeDisciplina, nomeProfessor, quantidadeAlunos, cargaHoraria, mediaTurma)
        )
        sucesso = cursor.rowcount > 0
        self.conexao.commit()
        cursor.close()
        return sucesso
    
    def buscar(self, codigo):
        cursor = self.conexao.cursor()
        cursor.execute('SELECT * FROM Materias WHERE codigo = ?', (codigo,))
        retorno = cursor.fetchone()
        cursor.close()
        return retorno
    
    def listarTodas(self):
        cursor = self.conexao.cursor()
        cursor.execute('SELECT * FROM Materias')
        retorno = cursor.fetchall()
        cursor.close()
        return retorno
    
    def update(self, codigoAntigo, codigoNovo, nomeDisciplina, nomeProfessor, quantidadeAlunos, cargaHoraria, mediaTurma):
        cursor = self.conexao.cursor()
        cursor.execute(
            "UPDATE Materias SET codigo = ?, nomeDisciplina = ?, nomeProfessor = ?, quantidadeAlunos = ?, cargaHoraria = ?, mediaTurma = ? WHERE codigo = ?",
            (codigoNovo, nomeDisciplina, nomeProfessor, quantidadeAlunos, cargaHoraria, mediaTurma, codigoAntigo)
        )
        sucesso = cursor.rowcount > 0
        self.conexao.commit()
        cursor.close()
        return sucesso
    
    def remover(self, codigo):
        cursor = self.conexao.cursor()

        # Antes remove todos alunos com relacao a disciplina
        cursor.execute('DELETE FROM Alunos WHERE codigoDisciplina = ?', (codigo,))

        # Depois remove a disciplina
        cursor.execute('DELETE FROM Materias WHERE codigo = ?', (codigo,))
        sucesso = cursor.rowcount > 0
        self.conexao.commit()
        cursor.close()
        return sucesso
    
    # Metodos para Alunos
    def contarAlunosDisciplina(self, codigoDisciplina):
        # Contar a quantidade de alunos na disciplina
        cursor = self.conexao.cursor()
        cursor.execute('SELECT COUNT(*) FROM Alunos WHERE codigoDisciplina = ?', (codigoDisciplina,))
        count = cursor.fetchone()[0]
        cursor.close()
        return count
    
    def adicionarAluno(self, nome, codigoDisciplina, nota):
        cursor = self.conexao.cursor()
        
        # Descobrir a quantidade maxima de alunos que pode ser adicionada
        cursor.execute('SELECT quantidadeAlunos FROM Materias WHERE codigo = ?', (codigoDisciplina,))
        resultado = cursor.fetchone()
        
        if resultado:
            qtd_maxima = resultado[0]
            qtd_atual = self.contarAlunosDisciplina(codigoDisciplina)
            
            # Verifica se ainda pode adicionar
            if qtd_atual >= qtd_maxima:
                cursor.close()
                return False  
        
        cursor.execute(
            "INSERT INTO Alunos(nome, codigoDisciplina, nota) VALUES(?, ?, ?)",
            (nome, codigoDisciplina, nota)
        )
        sucesso = cursor.rowcount > 0
        self.conexao.commit()
        cursor.close()
        return sucesso
    
    def buscarAluno(self, idAluno):
        cursor = self.conexao.cursor()
        cursor.execute('SELECT * FROM Alunos WHERE id = ?', (idAluno,))
        retorno = cursor.fetchone()
        cursor.close()
        return retorno
    
    def buscarAlunosPorDisciplina(self, codigoDisciplina):
        # Verifica se a disciplina existe antes de buscar alunos
        if not self.disciplinaExiste(codigoDisciplina):
            return None
        
        cursor = self.conexao.cursor()
        cursor.execute('SELECT * FROM Alunos WHERE codigoDisciplina = ?', (codigoDisciplina,))
        retorno = cursor.fetchall()
        cursor.close()
        return retorno
    
    def listarTodosAlunos(self):
        cursor = self.conexao.cursor()
        cursor.execute('SELECT * FROM Alunos')
        retorno = cursor.fetchall()
        cursor.close()
        return retorno
    
    def removerAluno(self, idAluno):
        cursor = self.conexao.cursor()
        cursor.execute('DELETE FROM Alunos WHERE id = ?', (idAluno,))
        sucesso = cursor.rowcount > 0
        self.conexao.commit()
        cursor.close()
        return sucesso
    
    def disciplinaExiste(self, codigo):
        cursor = self.conexao.cursor()
        cursor.execute('SELECT 1 FROM Materias WHERE codigo = ?', (codigo,))
        existe = cursor.fetchone() is not None
        cursor.close()
        return existe
    
    def disciplinaTemAlunos(self, codigo):
        cursor = self.conexao.cursor()
        cursor.execute('SELECT COUNT(*) FROM Alunos WHERE codigoDisciplina = ?', (codigo,))
        count = cursor.fetchone()[0]
        cursor.close()
        return count > 0
    
    def fecharConexao(self):
        if self.conexao:
            self.conexao.close()