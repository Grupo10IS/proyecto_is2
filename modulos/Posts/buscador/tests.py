import pytest

from modulos.Categories.models import Category
from modulos.Posts.buscador import buscador
from modulos.Posts.buscador.Nodes import (Node, NodeCategoria, NodeTags,
                                          NodeTitulo, QueryBuilder)
from modulos.Posts.buscador.parser import Parser
from modulos.Posts.buscador.tokenizer import (TOKEN_BEFORE, TOKEN_CATEGORIA,
                                              TOKEN_FILTER, TOKEN_NEGACION,
                                              TOKEN_SEPARATOR, TOKEN_TAGS,
                                              TOKEN_TEXT, TOKEN_TITULO, Lexer,
                                              Token)
from modulos.Posts.models import Post
from modulos.UserProfile.models import UserProfile

# ------------------------
# Test del query tokenizer
# ------------------------


def test_raw_token_generation():
    # Define los casos de prueba
    test_cases = [
        (
            " titulo vacio",
            [Token(TOKEN_TEXT, " titulo vacio")],
        ),
        (
            "#categoria:#titulo:",
            [
                Token(TOKEN_FILTER, "#"),
                Token(TOKEN_CATEGORIA, "categoria"),
                Token(TOKEN_SEPARATOR, ":"),
                Token(TOKEN_FILTER, "#"),
                Token(TOKEN_TITULO, "titulo"),
                Token(TOKEN_SEPARATOR, ":"),
            ],
        ),
        (
            "titulo # categoria  : nada",
            [
                Token(TOKEN_TITULO, "titulo "),
                Token(TOKEN_FILTER, "#"),
                Token(TOKEN_CATEGORIA, " categoria  "),
                Token(TOKEN_SEPARATOR, ":"),
                Token(TOKEN_TEXT, " nada"),
            ],
        ),
        (
            "Golang #tags: 1,2,3",
            [
                Token(TOKEN_TEXT, "Golang "),
                Token(TOKEN_FILTER, "#"),
                Token(TOKEN_TAGS, "tags"),
                Token(TOKEN_SEPARATOR, ":"),
                Token(TOKEN_TEXT, " 1,2,3"),
            ],
        ),
        (
            "#titulo: nuevo #tags: 1,2,3 #before: 12/12/12",
            [
                Token(TOKEN_FILTER, "#"),
                Token(TOKEN_TITULO, "titulo"),
                Token(TOKEN_SEPARATOR, ":"),
                Token(TOKEN_TEXT, " nuevo "),
                Token(TOKEN_FILTER, "#"),
                Token(TOKEN_TAGS, "tags"),
                Token(TOKEN_SEPARATOR, ":"),
                Token(TOKEN_TEXT, " 1,2,3 "),
                Token(TOKEN_FILTER, "#"),
                Token(TOKEN_BEFORE, "before"),
                Token(TOKEN_SEPARATOR, ":"),
                Token(TOKEN_TEXT, " 12/12/12"),
            ],
        ),
        (
            "#titulo!: nuevo",
            [
                Token(TOKEN_FILTER, "#"),
                Token(TOKEN_TITULO, "titulo"),
                Token(TOKEN_NEGACION, "!"),
                Token(TOKEN_SEPARATOR, ":"),
                Token(TOKEN_TEXT, " nuevo"),
            ],
        ),
    ]

    # Recorre cada caso de prueba
    count = 0
    for input_text, expected_tokens in test_cases:
        lexer = Lexer(input_text)
        lexer._generate_raw_tokens()

        result = lexer.tokens

        # Verifica que el número de tokens coincida
        if len(result) != len(expected_tokens):
            for t in result:
                print(t)
            assert f"TC: {count} \tExpected {len(expected_tokens)} tokens, but got {len(result)}."

        # Verifica que cada token coincida con el esperado
        for i in range(len(result)):
            if result[i].t_type != expected_tokens[i].t_type:
                print(f"\nExpected token {i}: \n{expected_tokens[i]}\n")
                print(f"Got: \n{result[i]}\n")

                assert (
                    False
                ), f"TC: {count} \tExpected token type {expected_tokens[i].t_type}, but got {result[i].t_type}."

            if result[i].t_value != expected_tokens[i].t_value:
                print(f"\nExpected token {i}: \n{expected_tokens[i]}\n")
                print(f"Got: \n{result[i]}")

                assert (
                    False
                ), f"TC: {count} \tExpected token type {expected_tokens[i].t_value}, but got {result[i].t_value}."

        count += 1


def test_token_sanitization():
    # Define los casos de prueba
    test_cases = [
        (
            " titulo vacio",
            [Token(TOKEN_TEXT, " titulo vacio")],
        ),
        (
            "#categoria:#titulo:",
            [
                Token(TOKEN_CATEGORIA, "categoria"),
                Token(TOKEN_TITULO, "titulo"),
            ],
        ),
        (
            "titulo # categoria nada",
            [
                Token(TOKEN_TEXT, "titulo "),
                Token(TOKEN_TEXT, "# categoria nada"),
            ],
        ),
        (
            "Golang #tags: 1,2,3",
            [
                Token(TOKEN_TEXT, "Golang "),
                Token(TOKEN_TAGS, "tags"),
                Token(TOKEN_TEXT, " 1,2,3"),
            ],
        ),
        (
            "#titulo!: nuevo",
            [
                Token(TOKEN_TITULO, "titulo"),
                Token(TOKEN_NEGACION, "!"),
                Token(TOKEN_TEXT, " nuevo"),
            ],
        ),
    ]

    # Recorre cada caso de prueba
    count = 0
    for input_text, expected_tokens in test_cases:
        lexer = Lexer(input_text)
        lexer._generate_raw_tokens()
        lexer._sanitize_tokens()

        result = lexer.tokens

        # Verifica que el número de tokens coincida
        if len(result) != len(expected_tokens):
            for t in result:
                print(t)
            assert f"TC: {count} \tExpected {len(expected_tokens)} tokens, but got {len(result)}."

        # Verifica que cada token coincida con el esperado
        for i in range(len(result)):
            if result[i].t_type != expected_tokens[i].t_type:
                print(f"\nExpected token {i}: \n{expected_tokens[i]}\n")
                print(f"Got: \n{result[i]}\n")

                assert (
                    False
                ), f"TC: {count} \tExpected token type {expected_tokens[i].t_type}, but got {result[i].t_type}."

            if result[i].t_value != expected_tokens[i].t_value:
                print(f"\nExpected token {i}: \n{expected_tokens[i]}\n")
                print(f"Got: \n{result[i]}")

                assert (
                    False
                ), f"TC: {count} \tExpected token type {expected_tokens[i].t_value}, but got {result[i].t_value}."

        count += 1


def test_text_squashing():
    # Define los casos de prueba
    test_cases = [
        (
            " titulo vacio",
            [Token(TOKEN_TEXT, " titulo vacio")],
        ),
        (
            "titulo # categoria nada",
            [
                Token(TOKEN_TEXT, "titulo # categoria nada"),
            ],
        ),
        (
            "Golang #tags: 1,2,3",
            [
                Token(TOKEN_TEXT, "Golang "),
                Token(TOKEN_TAGS, "tags"),
                Token(TOKEN_TEXT, " 1,2,3"),
            ],
        ),
        (
            "#titulo!: nuevo # nuevo personal",
            [
                Token(TOKEN_TITULO, "titulo"),
                Token(TOKEN_NEGACION, "!"),
                Token(TOKEN_TEXT, " nuevo # nuevo personal"),
            ],
        ),
    ]

    # Recorre cada caso de prueba
    count = 0
    for input_text, expected_tokens in test_cases:
        lexer = Lexer(input_text)

        lexer._generate_raw_tokens()
        lexer._sanitize_tokens()
        lexer._squash_text_tokens()

        result = lexer.tokens

        # Verifica que el número de tokens coincida
        if len(result) != len(expected_tokens):
            for t in result:
                print(t)
            assert f"TC: {count} \tExpected {len(expected_tokens)} tokens, but got {len(result)}."

        # Verifica que cada token coincida con el esperado
        for i in range(len(result)):
            if result[i].t_type != expected_tokens[i].t_type:
                print(f"\nExpected token {i}: \n{expected_tokens[i]}\n")
                print(f"Got: \n{result[i]}\n")

                assert (
                    False
                ), f"TC: {count} \tExpected token type {expected_tokens[i].t_type}, but got {result[i].t_type}."

            if result[i].t_value != expected_tokens[i].t_value:
                print(f"\nExpected token {i}: \n{expected_tokens[i]}\n")
                print(f"Got: \n{result[i]}")

                assert (
                    False
                ), f"TC: {count} \tExpected token type {expected_tokens[i].t_value}, but got {result[i].t_value}."

        count += 1


# ----------------------
# Test del query builder
# ----------------------


@pytest.fixture
def prepare(db):
    # Crea un usuario de prueba
    user1 = UserProfile.objects.create_user(
        username="alice", email="alice@example.com", password="password123"
    )
    user2 = UserProfile.objects.create_user(
        username="bob", email="bob@example.com", password="password123"
    )
    user3 = UserProfile.objects.create_user(
        username="johndoe", email="john@example.com", password="password123"
    )

    # Crea una categoría de prueba
    category = Category.objects.create(name="Django")

    # Configura datos de prueba
    post1 = Post.objects.create(
        title="Django for Beginners",
        author=user1,
        category=category,
        status=Post.PUBLISHED,
    )
    post2 = Post.objects.create(
        title="Advanced Django", author=user2, category=category, status=Post.DRAFT
    )
    post3 = Post.objects.create(
        title="Django Tips",
        author=user3,
        category=category,
        status=Post.PENDING_PUBLICATION,
    )

    return post1, post2, post3


def test_add_filter(prepare):
    post1, post2, post3 = prepare
    query_builder = QueryBuilder(Post)
    query_builder.add_filter(title__icontains="Django")
    results = query_builder.execute()

    assert post1 in results
    assert post2 in results
    assert post3 in results
    assert len(results) == 3


def test_add_not_filter(prepare):
    post1, post2, post3 = prepare
    query_builder = QueryBuilder(Post)
    query_builder.add_filter(title__icontains="Django").add_exclude(
        author__username="alice"
    )
    results = query_builder.execute()

    assert post1 not in results
    assert post2 in results
    assert post3 in results
    assert len(results) == 2


# ---------------
# Test del parser
# ---------------


def test_node_generation():
    # Define los casos de prueba
    test_cases: list[tuple[str, list[Node]]] = [
        (
            " titulo vacio",
            [NodeTitulo("titulo vacio", False)],
        ),
        (
            "titulo # categoria nada",
            [NodeTitulo("titulo # categoria nada", False)],
        ),
        (
            "Golang #tags: 1,2,3",
            [
                NodeTitulo("Golang", False),
                NodeTags("1,2,3", False),
            ],
        ),
        (
            "#titulo!: nuevo # nuevo personal",
            [
                NodeTitulo("nuevo # nuevo personal", True),
            ],
        ),
        (
            "#titulo!: nuevo # categoria : personal",
            [
                NodeTitulo("nuevo", True),
                NodeCategoria("personal", False),
            ],
        ),
    ]

    # Recorre cada caso de prueba
    count = 0
    for input_text, expected_nodes in test_cases:
        # Crear una nueva instancia de Lexer y Parser para cada caso de prueba
        lexer = Lexer(input_text)
        tokens = lexer.tokenize()

        # Crear una nueva instancia de Parser para cada caso de prueba
        parser = Parser(tokens)

        # Parsear los tokens
        result = parser.parse()

        # Verifica que el número de tokens coincida
        if len(result) != len(expected_nodes):
            for t in result:
                print(t)
            assert f"TC: {count} \tExpected {len(expected_nodes)} tokens, but got {len(result)}."

        # Verifica que cada token coincida con el esperado
        for i in range(len(result)):
            if result[i].value != expected_nodes[i].value:
                print(f"\nExpected Node {i}: \n{expected_nodes[i]}\n")
                print(f"Got: \n{result[i]}\n")

                assert (
                    False
                ), f"TC: {count} \tExpected Node value {expected_nodes[i].value}, but got {result[i].value}."

            if result[i].negation != expected_nodes[i].negation:
                print(f"\nExpected token {i}: \n{expected_nodes[i]}\n")
                print(f"Got: \n{result[i]}")

                assert (
                    False
                ), f"TC: {count} \tExpected token type {expected_nodes[i].negation}, but got {result[i].negation}."

            if result[i].n_type != expected_nodes[i].n_type:
                print(f"\nExpected node {i}: \n{expected_nodes[i]}\n")
                print(f"Got: \n{result[i]}")

                assert (
                    False
                ), f"TC: {count} \tExpected token type {expected_nodes[i].n_type}, but got {result[i].n_type}."

        count += 1


# ----------------------------
# Test ast -> query generator
# ----------------------------


def test_ast_to_query_generator(prepare):
    ## Test case numero 1 ###
    post1, post2, post3 = prepare

    qb = buscador.generate_query_set("Django")
    results = qb.execute()

    assert post1 in results
    assert post2 in results
    assert post3 in results
    assert len(results) == 3

    ## Test case numero 2 ###
    post1, post2, post3 = prepare

    qb = buscador.generate_query_set("Tips")
    results = qb.execute()

    assert post3 in results
    assert not post2 in results
    assert not post1 in results

    ## Test case numero 3 ###
    post1, post2, post3 = prepare

    qb = buscador.generate_query_set("Tips #autor: alice")
    results = qb.execute()

    assert not post3 in results
    assert not post2 in results
    assert not post1 in results

    ## Test case numero 4 ###
    post1, post2, post3 = prepare

    qb = buscador.generate_query_set("#autor!: alice")
    results = qb.execute()

    assert post3 in results
    assert post2 in results
    assert not post1 in results

    ## Test case numero 5 ###
    post1, post2, post3 = prepare

    qb = buscador.generate_query_set("Tips #categoria: Django")
    results = qb.execute()

    assert post3 in results
    assert not post2 in results
    assert not post1 in results
