### TOKEN TYPES ###

# Palabras clave
TOKEN_CATEGORIA = "categoria"
TOKEN_TITULO = "titulo"
TOKEN_CONTENIDO = "contenido"
TOKEN_AUTOR = "autor"
TOKEN_TAGS = "tags"
TOKEN_AFTER = "after"
TOKEN_BEFORE = "before"

# Operadores
TOKEN_FILTER = "#"
TOKEN_NEGACION = "!"
TOKEN_SEPARATOR = ":"

# Tipos de tokens
TOKEN_TEXT = "text"  # Texto que puede tener múltiples palabras
TOKEN_INVALIDO = "invalido"  # Token inválido

# Listado de palabras clave y operadores reconocidos
PALABRAS_CLAVE = {
    TOKEN_CATEGORIA: TOKEN_CATEGORIA,
    TOKEN_TITULO: TOKEN_TITULO,
    TOKEN_CONTENIDO: TOKEN_CONTENIDO,
    TOKEN_AUTOR: TOKEN_AUTOR,
    TOKEN_TAGS: TOKEN_TAGS,
    TOKEN_AFTER: TOKEN_AFTER,
    TOKEN_BEFORE: TOKEN_BEFORE,
}

CARACTERES_ESPECIALES = {
    TOKEN_FILTER: TOKEN_FILTER,
    TOKEN_NEGACION: TOKEN_NEGACION,
    TOKEN_SEPARATOR: TOKEN_SEPARATOR,
}


def resolve_type(text: str):
    """
    Determina el tipo de token según el texto proporcionado.

    Args:
        text (str): Texto que representa un posible token.

    Returns:
        str: Tipo de token correspondiente.
    """
    text = text.strip()

    if text in PALABRAS_CLAVE:
        return PALABRAS_CLAVE[text]

    if text in CARACTERES_ESPECIALES:
        return CARACTERES_ESPECIALES[text]

    # Por defecto, todo se considera un token de texto.
    return TOKEN_TEXT


def is_letter(ch):
    """
    Comprueba si un carácter es una letra o un guion bajo.

    Args:
        ch (str): Carácter a verificar.

    Returns:
        bool: True si el carácter es una letra o un guion bajo, False en caso contrario.
    """
    return not ch in CARACTERES_ESPECIALES and ch != ""


class Token:
    t_type: str
    t_value: str

    def __str__(self):
        return f"Token(t_type='{self.t_type}', t_value='{self.t_value}')"

    def __init__(self, t, value):
        """
        Constructor para inicializar un nuevo token.

        Args:
            t (str): Tipo del token.
            value (str): Valor asociado al token.
        """
        self.t_type = t
        self.t_value = value


class Lexer:
    curr_position = -1  # Posición actual del lexer en la cadena
    next_position = 0  # Próxima posición del lexer en la cadena

    curr_char = ""  # Carácter actual procesado
    parsing_string = ""  # Cadena que se está analizando

    tokens: list[Token]

    def _generate_raw_tokens(self):
        """
        Analiza la cadena completa y genera una lista de tokens.

        Returns:
            list[Token]: Lista de tokens encontrados en la cadena de entrada.
        """

        result: list[Token] = []

        while self.curr_char != "":
            # Caracteres especiales
            if self.curr_char in CARACTERES_ESPECIALES:
                t = Token(resolve_type(self.curr_char), self.curr_char)
                result.append(t)
                self._advance_lexer()

            # Tokens multi carácter
            else:
                t = self._parse_text()
                result.append(t)

        self.tokens = result

    def _squash_text_tokens(self):
        token_count = -1
        new_list: list[Token] = []

        for token in self.tokens:
            if token.t_type != TOKEN_TEXT:
                new_list.append(token)
                token_count += 1

                # si contamos con 2 tokens de texto seguidos
            elif (
                token_count > -1  # revisar que ya se haya insertado un token
                and new_list[token_count].t_type == TOKEN_TEXT
                and token.t_type == TOKEN_TEXT
            ):
                new_list[token_count].t_value += token.t_value

                # si es el primer token de texto en ser insertado depues de un filtro o al inicio
            else:
                new_list.append(token)
                token_count += 1

        self.tokens = new_list

    def _sanitize_tokens(self):
        curr_position = 0
        new_list: list[Token] = []

        while curr_position < len(self.tokens):
            # si encontramos un token de filtro revisar que tenga la sintaxis correcta.
            # Transformar a token de texto si es que no se sigue la sintaxis
            # "# identificador [!]:"
            if self.tokens[curr_position].t_type == TOKEN_FILTER:
                if (
                    curr_position + 2 < len(self.tokens)
                    and self.tokens[curr_position + 2].t_type == TOKEN_SEPARATOR
                    and self.tokens[curr_position + 1].t_type in PALABRAS_CLAVE
                ):
                    # solo anadir el token de "palabra clave"
                    new_list.append(self.tokens[curr_position + 1])
                    curr_position += 3
                    continue

                if (
                    curr_position + 3 < len(self.tokens)
                    and self.tokens[curr_position + 2].t_type == TOKEN_NEGACION
                    and self.tokens[curr_position + 3].t_type == TOKEN_SEPARATOR
                    and self.tokens[curr_position + 1].t_type in PALABRAS_CLAVE
                ):
                    # solo anadir el token de "palabra clave" y el de negacion
                    new_list.append(self.tokens[curr_position + 1])
                    new_list.append(self.tokens[curr_position + 2])
                    curr_position += 4
                    continue

                # si la sintaxis NO fue correcta, cambiamos el token a
                # un token de tipo texto
                self.tokens[curr_position].t_type = TOKEN_TEXT

            # Unir los tokens en un solo token de texto hasta el siguiente token de filtro
            value = ""
            while (
                curr_position < len(self.tokens)
                and self.tokens[curr_position].t_type != TOKEN_FILTER
            ):
                value += self.tokens[curr_position].t_value
                curr_position += 1

            new_list.append(Token(TOKEN_TEXT, value))

        self.tokens = new_list

    def tokenize(self):
        self._generate_raw_tokens()
        self._sanitize_tokens()
        self._squash_text_tokens()

        return self.tokens

    def __init__(self, s) -> None:
        """
        Inicializa el lexer con la cadena de entrada.

        Args:
            s (str): Cadena que se va a analizar.
        """
        self.parsing_string = s
        self._advance_lexer()

    # -------------------
    # -    Utilities    -
    # -------------------

    def _pick_char(self):
        """
        Obtiene el siguiente carácter a procesar sin avanzar el lexer.

        Returns:
            str: Próximo carácter de la cadena.
        """
        if self.curr_position >= len(self.parsing_string):
            return 0

        return self.parsing_string[self.curr_position + 1]

    def _advance_lexer(self):
        """
        Avanza el lexer a la siguiente posición de la cadena.
        """
        if self.next_position >= len(self.parsing_string):
            self.curr_char = ""
        else:
            self.curr_char = self.parsing_string[self.next_position]

        self.curr_position = self.next_position
        self.next_position = self.next_position + 1

    def _parse_text(self) -> Token:
        """
        Analiza y crea un token de texto (multicaracter) desde la posición actual del lexer.

        Returns:
            Token: El token creado con su tipo y valor.
        """
        start = self.curr_position

        while is_letter(self.curr_char):
            self._advance_lexer()

        value = self.parsing_string[start : self.curr_position]

        return Token(resolve_type(value), value)

    def __str__(self):
        return (
            f"Lexer State:\n"
            f"  Current Position: {self.curr_position}\n"
            f"  Next Position: {self.next_position}\n"
            f"  Current Char: '{self.curr_char}'\n"
            f"  Parsing String: '{self.parsing_string}'"
        )
