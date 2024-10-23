from modulos.Posts.buscador.Nodes import (NODES_TABLE, Node, NodeTitulo,
                                          QueryBuilder)
from modulos.Posts.buscador.tokenizer import TOKEN_NEGACION, TOKEN_TEXT, Token
from modulos.Posts.models import Post


class Parser(object):
    tokens: list[Token]
    qb: QueryBuilder

    curr_position = -1
    next_position = 0
    curr_token: Token

    ast: list[Node]

    def __init__(self, tokens: list[Token]) -> None:
        self.tokens = tokens
        self._advance_parser()
        self.ast = []

    def parse(self):
        if len(self.tokens) == 0:
            return self.ast

        # cuando el primero token es un texto, entonces debemos generar un nodo titulo
        if self.curr_token.t_type == TOKEN_TEXT:
            self.ast.append(NodeTitulo(self.curr_token.t_value))
            self._advance_parser()

        # ahora el resto de tokens
        while self.curr_position < len(self.tokens):
            node_type = NODES_TABLE[self.curr_token.t_type]
            negacion = False

            # si el siguiente token es una negacion entonces avanzar
            next_token = self._pick_token()
            if next_token != None and next_token.t_type == TOKEN_NEGACION:
                self._advance_parser()
                negacion = True

            # extraemos el valor del token que precede a un filtro
            self._advance_parser()
            if self.curr_token != None and self.curr_token.t_type == TOKEN_TEXT:
                node = node_type(self.curr_token.t_value, negacion)
                self.ast.append(node)

            self._advance_parser()

        return self.ast

    # -------------
    # - Utilities -
    # -------------

    def _pick_token(self) -> Token | None:
        """
        Devuelve los siguientes "n" tokens dentro de la lista de tokens proveidas
        por el tokenizer. Si no se proporciona ningun valor para N entonces se utilizara n=1.

        Return:
            Un objeto Token. En caso de que no existan mas tokens para consumir se retornara None.
        """
        if self.curr_position + 1 >= len(self.tokens):
            return None

        return self.tokens[self.curr_position + 1]

    def _advance_parser(self):
        self.curr_position = self.next_position
        self.next_position += 1

        if self.curr_position >= len(self.tokens):
            return

        self.curr_token = self.tokens[self.curr_position]
