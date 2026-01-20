import cherrypy
import Banco  

@cherrypy.expose
class CRUD:
    def __init__(self):
        self.banco = Banco.Banco()

    # Metodos para as Disciplinas    
    # POST
    def adicionar(self, **kwargs):
        chaves = {"codigo", "nomeDisciplina", "nomeProfessor", "quantidadeAlunos", "cargaHoraria", "mediaTurma"}
        if set(kwargs.keys()).issuperset(chaves):
            try:
                # Verificando campos 
                if not kwargs["codigo"].strip():
                    raise cherrypy.HTTPError(422, "Codigo nao pode ser vazio.")
                if not kwargs["nomeDisciplina"].strip():
                    raise cherrypy.HTTPError(422, "Nome da disciplina nao pode ser vazio.")
                if not kwargs["nomeProfessor"].strip():
                    raise cherrypy.HTTPError(422, "Nome do professor nao pode ser vazio.")
                
                qtd_alunos = int(kwargs["quantidadeAlunos"])
                carga = int(kwargs["cargaHoraria"])
                media = float(kwargs["mediaTurma"])
                
                if qtd_alunos < 0:
                    raise cherrypy.HTTPError(422, "Quantidade de alunos nao pode ser negativa.")
                if carga <= 0:
                    raise cherrypy.HTTPError(422, "Carga horaria deve ser maior que zero.")
                if media < 0 or media > 10:
                    raise cherrypy.HTTPError(422, "Media deve estar entre 0 e 10.")
                
                sucesso = self.banco.adicionar(
                    kwargs["codigo"],
                    kwargs["nomeDisciplina"],
                    kwargs["nomeProfessor"],
                    qtd_alunos,
                    carga,
                    media
                )
                if sucesso:
                    cherrypy.response.status = 201
                    return f"<div>Disciplina '{kwargs['nomeDisciplina']}' adicionada com sucesso.</div>"
                else:
                    raise cherrypy.HTTPError(500, "Falha ao inserir no banco.")
            except ValueError:
                raise cherrypy.HTTPError(422, "Algum valor inserido invalido.")
        else:
            raise cherrypy.HTTPError(400, "Faltou alguma chave.")
    
    # GET 
    def buscar(self, codigo=None, **kwargs): #  Busca uma ou lista todas
        if codigo:
            tupla = self.banco.buscar(codigo)
            if tupla:
                msg = f"<div>Código: {tupla[0]}<br>Nome: {tupla[1]}<br>Professor: {tupla[2]}<br>Alunos: {tupla[3]}<br>Carga Horária: {tupla[4]}<br>Média: {tupla[5]}</div>"
                return msg
            else:
                raise cherrypy.HTTPError(404, "Disciplina nao encontrada.")
        else:
            lista = self.banco.listarTodas()
            mensagem = "<div>Lista de disciplinas: </div>"
            for t in lista:
                mensagem += f"<div>Código: {t[0]}<br>Nome: {t[1]}<br>Professor: {t[2]}<br>Alunos: {t[3]}<br>Carga Horária: {t[4]}<br>Média: {t[5]}</div>"
            return mensagem

    # PUT - Atualizar disciplina
    def atualizar(self, codigoAntigo, **kwargs):
        chaves = {"codigo", "nomeDisciplina", "nomeProfessor", "quantidadeAlunos", "cargaHoraria", "mediaTurma"}
        if set(kwargs.keys()).issuperset(chaves):
            try:
                # Verificando campos 
                if not kwargs["codigo"].strip():
                    raise cherrypy.HTTPError(422, "Codigo nao pode ser vazio.")
                if not kwargs["nomeDisciplina"].strip():
                    raise cherrypy.HTTPError(422, "Nome da disciplina nao pode ser vazio.")
                if not kwargs["nomeProfessor"].strip():
                    raise cherrypy.HTTPError(422, "Nome do professor nao pode ser vazio.")
            
                qtd_alunos = int(kwargs["quantidadeAlunos"])
                carga = int(kwargs["cargaHoraria"])
                media = float(kwargs["mediaTurma"])
                
                if qtd_alunos < 0:
                    raise cherrypy.HTTPError(422, "Quantidade de alunos nao pode ser negativa.")
                if carga <= 0:
                    raise cherrypy.HTTPError(422, "Carga horaria deve ser maior que zero.")
                if media < 0 or media > 10:
                    raise cherrypy.HTTPError(422, "Media deve estar entre 0 e 10.")
                
                # Nao atualiza se a quantidade de alunos for menor que a de antes
                qtd_atual_alunos = self.banco.contarAlunosDisciplina(codigoAntigo)
                if qtd_alunos < qtd_atual_alunos:
                    raise cherrypy.HTTPError(422, 
                        f"Nao e possivel reduzir para {qtd_alunos} alunos. Ja existem {qtd_atual_alunos} alunos cadastrados nesta disciplina.")
                
                sucesso = self.banco.update(
                    codigoAntigo,
                    kwargs["codigo"],
                    kwargs["nomeDisciplina"],
                    kwargs["nomeProfessor"],
                    qtd_alunos,
                    carga,
                    media
                )
                
                if sucesso:
                    cherrypy.response.status = 200
                    return f"<div>Disciplina '{codigoAntigo}' atualizada com sucesso.</div>"
                else:
                    raise cherrypy.HTTPError(404, "Disciplina nao encontrada para atualizar.")
                    
            except ValueError:
                raise cherrypy.HTTPError(422, "Erro de tipo nos dados enviados. Verifique se os numeros estao corretos.")
        else:
            raise cherrypy.HTTPError(400, "Faltam campos para requisicao.")

    # DELETE 
    def remover(self, codigo, **kwargs):
        sucesso = self.banco.remover(codigo)
        if sucesso:
            cherrypy.response.status = 200
            return f"<div>Disciplina '{codigo}' removida com sucesso.</div>"
        else:
            raise cherrypy.HTTPError(404, "Disciplina nao encontrada para remover.")

    # POST - Adicionar aluno
    def adicionarAluno(self, **kwargs):
        chaves = {"nome", "codigoDisciplina", "nota"}
        if set(kwargs.keys()).issuperset(chaves):
            try:
                if not kwargs["nome"].strip():
                    raise cherrypy.HTTPError(422, "Nome do aluno nao pode ser vazio.")
                if not self.banco.disciplinaExiste(kwargs["codigoDisciplina"]):
                    raise cherrypy.HTTPError(404, "Disciplina nao encontrada.")

                nota = float(kwargs["nota"])
                if nota < 0 or nota > 10:
                    raise cherrypy.HTTPError(422, "Nota deve estar entre 0 e 10.")
                
                sucesso = self.banco.adicionarAluno(kwargs["nome"], kwargs["codigoDisciplina"], nota)
                if sucesso:
                    cherrypy.response.status = 201
                    return f"<div>Aluno '{kwargs['nome']}' adicionado com sucesso.</div>"
                else:
                    # Busca informações da disciplina para mensagem de erro mais informativa
                    disciplina = self.banco.buscar(kwargs["codigoDisciplina"])
                    if disciplina:
                        qtd_atual = self.banco.contarAlunosDisciplina(kwargs["codigoDisciplina"])
                        raise cherrypy.HTTPError(422, 
                            f"Limite de alunos atingido. Disciplina permite {disciplina[3]} alunos e ja possui {qtd_atual} cadastrados.")
                    else:
                        raise cherrypy.HTTPError(500, "Falha ao adicionar aluno.")
            except ValueError:
                raise cherrypy.HTTPError(422, "Nota invalida.")
        else:
            raise cherrypy.HTTPError(400, "Faltam campos obrigatorios.")

    # GET - Buscar alunos
    def buscarAluno(self, codigoDisciplina=None, **kwargs):
        if codigoDisciplina:
            alunos = self.banco.buscarAlunosPorDisciplina(codigoDisciplina)
            if alunos is None:
                raise cherrypy.HTTPError(404, "Disciplina nao encontrada.")
            if alunos:
                mensagem = f"<div>Alunos da disciplina {codigoDisciplina}:</div>"
                for a in alunos:
                    mensagem += f"<div>ID: {a[0]}, Nome: {a[1]}, Nota: {a[3]}</div>"
                return mensagem
            else:
                raise cherrypy.HTTPError(404, "Nenhum aluno encontrado nesta disciplina.")
        else:
            alunos = self.banco.listarTodosAlunos()
            mensagem = "<div>Todos os alunos:</div>"
            for a in alunos:
                mensagem += f"<div>ID: {a[0]}, Nome: {a[1]}, Disciplina: {a[2]}, Nota: {a[3]}</div>"
            return mensagem

    # DELETE
    def removerAluno(self, id, **kwargs):
        sucesso = self.banco.removerAluno(id)
        if sucesso:
            cherrypy.response.status = 200
            return f"<div>Aluno com ID '{id}' removido com sucesso.</div>"
        else:
            raise cherrypy.HTTPError(404, "Aluno não encontrado.")



@cherrypy.expose
class Root:
    def index(self):
        return """
        <html>
        <head><title>API de Disciplinas</title></head>
        <body>
            <h1>API REST - Sistema de Disciplinas</h1>
            <h2>Endpoints disponiveis:</h2>
            
            <h3>Disciplinas</h3>
            <ul>
                <li><strong>GET</strong> /disciplinas - Listar todas as disciplinas</li>
                <li><strong>GET</strong> /disciplinas/{codigo} - Buscar disciplina por código</li>
                <li><strong>POST</strong> /disciplinas - Adicionar nova disciplina</li>
                <li><strong>PUT</strong> /disciplinas/{codigoAntigo} - Atualizar disciplina</li>
                <li><strong>DELETE</strong> /disciplinas/{codigo} - Remover disciplina</li>
            </ul>
            
            <h3>Alunos</h3>
            <ul>
                <li><strong>GET</strong> /alunos - Listar todos os alunos</li>
                <li><strong>GET</strong> /alunos/{codigoDisciplina} - Buscar alunos de uma disciplina</li>
                <li><strong>POST</strong> /alunos - Adicionar novo aluno</li>
                <li><strong>DELETE</strong> /alunos/{id} - Remover aluno</li>
            </ul>
        </body>
        </html>
        """


def main():
    banco = Banco.Banco()
    root = Root()
    c = CRUD()
    
    despachante = cherrypy.dispatch.RoutesDispatcher()

    # Rota Raiz
    despachante.connect(name='home', route='/', controller=root, action='index', conditions=dict(method=['GET']))

    # Parte das Disciplinas
    despachante.connect(name='adicionar', route='/disciplinas', controller=c, action='adicionar', conditions=dict(method=['POST']))
    despachante.connect(name='listar', route='/disciplinas', controller=c, action='buscar', conditions=dict(method=['GET']))
    despachante.connect(name='buscar', route='/disciplinas/:codigo', controller=c, action='buscar', conditions=dict(method=['GET']))
    despachante.connect(name='atualizar', route='/disciplinas/:codigoAntigo', controller=c, action='atualizar', conditions=dict(method=['PUT']))
    despachante.connect(name='remover', route='/disciplinas/:codigo', controller=c, action='remover', conditions=dict(method=['DELETE']))
    
    # Alunos
    despachante.connect(name='adicionarAluno', route='/alunos', controller=c, action='adicionarAluno', conditions=dict(method=['POST']))
    despachante.connect(name='listarAlunos', route='/alunos', controller=c, action='buscarAluno', conditions=dict(method=['GET']))
    despachante.connect(name='buscarAlunosDisciplina', route='/alunos/:codigoDisciplina', controller=c, action='buscarAluno', conditions=dict(method=['GET']))
    despachante.connect(name='removerAluno', route='/alunos/:id', controller=c, action='removerAluno', conditions=dict(method=['DELETE']))

    conf = {'/': {'request.dispatch': despachante}}
    cherrypy.tree.mount(None, config=conf)
    cherrypy.config.update({'server.socket_port': 8080})
    cherrypy.engine.start()
    cherrypy.engine.block()

if __name__ == "__main__":
    main()