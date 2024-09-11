from modulos.Posts.buscador.buscador import QueryBuilder
from modulos.Posts.buscador.tokenizer import Token


class Node:
    token: str

    def _generate_query(self, qb: QueryBuilder):
        pass


class NodeCategoria(Node):
    left: Token
    right: Node

    def _generate_query(self, qb: QueryBuilder):
        qb.add_filter(title__icontains="django").add_filter(author__name="John Doe")


class NodeTitulo(Node):
    left: Token
    right: Node

    def _generate_query(self, qb: QueryBuilder):
        qb.add_filter(title__icontains="django").add_filter(author__name="John Doe")


class NodeContenido(Node):
    left: Token
    right: Node

    def _generate_query(self, qb: QueryBuilder):
        qb.add_filter(title__icontains="django").add_filter(author__name="John Doe")


class NodeAutor(Node):
    left: Token
    right: Node

    def _generate_query(self, qb: QueryBuilder):
        qb.add_filter(title__icontains="django").add_filter(author__name="John Doe")


class NodeTags(Node):
    left: Token
    right: Node

    def _generate_query(self, qb: QueryBuilder):
        qb.add_filter(title__icontains="django").add_filter(author__name="John Doe")


class NodeAfter(Node):
    left: Token
    right: Node

    def _generate_query(self, qb: QueryBuilder):
        qb.add_filter(title__icontains="django").add_filter(author__name="John Doe")


class NodeBefore(Node):
    left: Token
    right: Node

    def _generate_query(self, qb: QueryBuilder):
        qb.add_filter(title__icontains="django").add_filter(author__name="John Doe")


class NodeText(Node):
    left: Token
    right: Node

    def _generate_query(self, qb: QueryBuilder):
        qb.add_filter(title__icontains="django").add_filter(author__name="John Doe")
