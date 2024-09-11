from django.db.models import Q, QuerySet

from modulos.Posts.buscador.tokenizer import (TOKEN_FILTER, TOKEN_NEGACION,
                                              TOKEN_SEPARATOR, TOKEN_TEXT,
                                              Lexer, Token)
from modulos.Posts.models import Post


class QueryBuilder:
    def __init__(self, model):
        self.model = model
        self.filters = (
            Q()
        )  # Utilizamos un objeto Q para construir los filtros dinámicamente

    def add_filter(self, **kwargs):
        # Agrega un filtro basado en los argumentos recibidos
        self.filters &= Q(**kwargs)
        return self

    def add_exclude(self, **kwargs):
        # Agrega un filtro de exclusión
        self.filters &= ~Q(**kwargs)
        return self

    def execute(self):
        # Ejecuta la consulta sobre el modelo
        return self.model.objects.filter(self.filters)


class Parser(object):
    tokens: list[Token]
    qb: QueryBuilder

    curr_position = -1
    next_position = 0
    curr_token: Token

    def __init__(self, tokens: list[Token]) -> None:
        self.QueryBuilder = QueryBuilder(Post)
        self.tokens = tokens
        self._advance_parser()

    def _pick_n_tokens(self, n) -> Token | None:
        if self.curr_position + n >= len(self.tokens):
            return None

        return self.tokens[self.curr_position + n]

    def _advance_parser(self):
        if self.next_position >= len(self.tokens):
            return None

        self.curr_position = self.next_position
        self.next_position += 1
        self.curr_token = self.tokens[self.curr_position]

    def parse_text(self):
        # TODO: continuar
        pass

    def parse_filter(self):
        if (
            self._pick_n_tokens(1) == TOKEN_NEGACION
            and self._pick_n_tokens(2) == TOKEN_SEPARATOR
        ):

            return

    def parse(self):
        # if the first token is a text token, then parse it until we found a filter token
        if self.curr_token.t_type == TOKEN_TEXT:
            self.qb.add_filter(title__icontains=self.curr_token.t_value)
            self._advance_parser()

        # ahora nunca se deberia de volver a acceder a este punto
        if self.curr_token.t_type == TOKEN_FILTER:
            self.parse_filter()

        return self.qb


def new_parser_from_input(input: str):
    return Parser(Lexer(input).generate_tokens())
