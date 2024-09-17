from django.db.models import Q

from modulos.Posts.buscador.tokenizer import *


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


# The base Node class
class Node:
    value: str
    negation: bool
    n_type: str

    def _generate_query(self, qb: QueryBuilder):
        pass

    def __init__(self, value: str, negation: bool = False) -> None:
        self.value = value.strip()
        self.negation = negation

    def __str__(self) -> str:
        return f"<{self.value}, negation={self.negation}, type={self.n_type}>"


class NodeCategoria(Node):
    n_type = "categoria"

    def _generate_query(self, qb: QueryBuilder):
        # TODO: cambiar el query builder para agregar negaciones
        qb.add_filter(title__icontains="django").add_filter(author__name="John Denver")


class NodeTitulo(Node):
    n_type = "titulo"

    def _generate_query(self, qb: QueryBuilder):
        qb.add_filter(title__icontains="django").add_filter(author__name="John Doe")


class NodeContenido(Node):
    n_type = "contenido"

    def _generate_query(self, qb: QueryBuilder):
        qb.add_filter(title__icontains="django").add_filter(author__name="John Doe")


class NodeAutor(Node):
    n_type = "autor"

    def _generate_query(self, qb: QueryBuilder):
        qb.add_filter(title__icontains="django").add_filter(author__name="John Doe")


class NodeTags(Node):
    n_type = "tags"

    def _generate_query(self, qb: QueryBuilder):
        qb.add_filter(title__icontains="django").add_filter(author__name="John Doe")


class NodeAfter(Node):
    n_type = "after"

    def _generate_query(self, qb: QueryBuilder):
        qb.add_filter(title__icontains="django").add_filter(author__name="John Doe")


class NodeBefore(Node):
    n_type = "before"

    def _generate_query(self, qb: QueryBuilder):
        qb.add_filter(title__icontains="django").add_filter(author__name="John Doe")


NODES_TABLE = {
    TOKEN_CATEGORIA: NodeCategoria,
    TOKEN_TAGS: NodeTags,
    TOKEN_BEFORE: NodeBefore,
    TOKEN_AFTER: NodeAfter,
    TOKEN_TITULO: NodeTitulo,
    TOKEN_CONTENIDO: NodeContenido,
    TOKEN_AUTOR: NodeAutor,
}
