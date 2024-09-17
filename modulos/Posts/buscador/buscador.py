from modulos.Posts.buscador.Nodes import QueryBuilder
from modulos.Posts.buscador.parser import Parser
from modulos.Posts.buscador.tokenizer import Lexer
from modulos.Posts.models import Post


def generate_query_set(input: str):
    tokens = Lexer(input).tokenize()
    nodes = Parser(tokens).parse()

    query_list = []
    qb = QueryBuilder(Post)

    for n in nodes:
        query_list.append(n._generate_query(qb))

    return qb
