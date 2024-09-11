import pytest

from modulos.Categories.models import Category
from modulos.Posts.buscador.buscador import QueryBuilder
from modulos.Posts.buscador.tokenizer import (TOKEN_BEFORE, TOKEN_CATEGORIA,
                                              TOKEN_COMMA, TOKEN_FILTER,
                                              TOKEN_NEGACION, TOKEN_SEPARATOR,
                                              TOKEN_TAGS, TOKEN_TEXT,
                                              TOKEN_TITULO, Lexer, Token)
from modulos.Posts.models import Post
from modulos.UserProfile.models import UserProfile

# ------------------------
# Test del query tokenizer
# ------------------------


def test_lexer():
    # Define los casos de prueba
    test_cases = [
        (
            " titulo vacio",
            [Token(TOKEN_TEXT, "titulo vacio")],
        ),
        (
            "titulo # categoria  : nada",
            [
                Token(TOKEN_TITULO, "titulo"),
                Token(TOKEN_FILTER, "#"),
                Token(TOKEN_CATEGORIA, "categoria"),
                Token(TOKEN_SEPARATOR, ":"),
                Token(TOKEN_TEXT, "nada"),
            ],
        ),
        (
            "Golang #tags: 1,2,3",
            [
                Token(TOKEN_TEXT, "Golang"),
                Token(TOKEN_FILTER, "#"),
                Token(TOKEN_TAGS, "tags"),
                Token(TOKEN_SEPARATOR, ":"),
                Token(TOKEN_TEXT, "1"),
                Token(TOKEN_COMMA, ","),
                Token(TOKEN_TEXT, "2"),
                Token(TOKEN_COMMA, ","),
                Token(TOKEN_TEXT, "3"),
            ],
        ),
        (
            "#titulo: nuevo #tags: 1,2,3 #before: 12/12/12",
            [
                Token(TOKEN_FILTER, "#"),
                Token(TOKEN_TITULO, "titulo"),
                Token(TOKEN_SEPARATOR, ":"),
                Token(TOKEN_TEXT, "nuevo"),
                Token(TOKEN_FILTER, "#"),
                Token(TOKEN_TAGS, "tags"),
                Token(TOKEN_SEPARATOR, ":"),
                Token(TOKEN_TEXT, "1"),
                Token(TOKEN_COMMA, ","),
                Token(TOKEN_TEXT, "2"),
                Token(TOKEN_COMMA, ","),
                Token(TOKEN_TEXT, "3"),
                Token(TOKEN_FILTER, "#"),
                Token(TOKEN_BEFORE, "before"),
                Token(TOKEN_SEPARATOR, ":"),
                Token(TOKEN_TEXT, "12/12/12"),
            ],
        ),
        (
            "#titulo!: nuevo",
            [
                Token(TOKEN_FILTER, "#"),
                Token(TOKEN_TITULO, "titulo"),
                Token(TOKEN_NEGACION, "!"),
                Token(TOKEN_SEPARATOR, ":"),
                Token(TOKEN_TEXT, "nuevo"),
            ],
        ),
    ]

    # Recorre cada caso de prueba
    count = 0
    for input_text, expected_tokens in test_cases:
        lexer = Lexer(input_text)
        result = lexer.generate_tokens()

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
        title="Django Tips", author=user3, category=category, status=Post.REJECTED
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
# Test del Parser
# ---------------


