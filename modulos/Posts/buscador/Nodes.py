from datetime import datetime

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
        return self.model.objects.filter(self.filters, active=True)


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
        if self.negation:
            qb.add_exclude(category__name__icontains=self.value)
        else:
            qb.add_filter(category__name__icontains=self.value)


class NodeTitulo(Node):
    n_type = "titulo"

    def _generate_query(self, qb: QueryBuilder):
        if self.negation:
            qb.add_exclude(title__icontains=self.value)
        else:
            qb.add_filter(title__icontains=self.value)


class NodeContenido(Node):
    n_type = "contenido"

    def _generate_query(self, qb: QueryBuilder):
        if self.negation:
            qb.add_exclude(content__icontains=self.value)
        else:
            qb.add_filter(content__icontains=self.value)


class NodeAutor(Node):
    n_type = "autor"

    def _generate_query(self, qb: QueryBuilder):
        if self.negation:
            qb.add_exclude(author__username__icontains=self.value)
        else:
            qb.add_filter(author__username__icontains=self.value)


class NodeTags(Node):
    n_type = "tags"

    def _generate_query(self, qb: QueryBuilder):
        tags = self.value.split(",")
        for tag in tags:
            if self.negation:
                qb.add_exclude(tags__icontains=tag)
            else:
                qb.add_filter(tags__icontains=tag)


class NodeAfter(Node):
    n_type = "after"

    def _generate_query(self, qb: QueryBuilder):
        # NOTE: negacion no tiene efecto sobre after
        try:
            fecha = datetime.strptime(self.value, "%d/%m/%Y")
            qb.add_filter(creation_date__gte=fecha)
        except ValueError:
            # Formato de fecha invalido
            return None


class NodeBefore(Node):
    n_type = "before"

    def _generate_query(self, qb: QueryBuilder):
        # NOTE: negacion no tiene efecto sobre before
        fecha = datetime.strptime(self.value, "%d/%m/%Y")
        try:
            fecha = datetime.strptime(self.value, "%d/%m/%Y")
            qb.add_filter(creation_date__lte=fecha)
        except ValueError:
            # Formato de fecha invalido
            return None


NODES_TABLE = {
    TOKEN_CATEGORIA: NodeCategoria,
    TOKEN_TAGS: NodeTags,
    TOKEN_BEFORE: NodeBefore,
    TOKEN_AFTER: NodeAfter,
    TOKEN_TITULO: NodeTitulo,
    TOKEN_CONTENIDO: NodeContenido,
    TOKEN_AUTOR: NodeAutor,
}
