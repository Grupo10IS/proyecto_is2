from modulos.UserProfile.management.commands.new_admin import (
    _credentials, has_valid_credentials)


def test_admin_credentials_validation():
    """
    Testear que no se acepten credenciales invalidas en la funcion de creacion
    de admin
    """

    test_cases = [
        (
            _credentials(
                username="Usuario invalido",
                email="email_invalido",
                paswd="contrasenha corta",
                pas_conf="contrasenha no es igual",
            ),
            False,
            "Debe dar error porque el usuario contiene espacios",
        ),
        (
            _credentials(
                username="Usuario_valido",
                email="email_invalido",
                paswd="contrasenha corta",
                pas_conf="contrasenha no es igual",
            ),
            False,
            "Debe dar error porque el email es invalido",
        ),
        (
            _credentials(
                username="Usuario_valido",
                email="email@valido.com",
                paswd="124",
                pas_conf="contrasenha distinta",
            ),
            False,
            "Debe dar error porque las contrasenhas no son iguales",
        ),
        (
            _credentials(
                username="Usuario_valido",
                email="email@valido.com",
                paswd="124",
                pas_conf="124",
            ),
            True,
            "Usuario Valido !!!",
        ),
    ]

    i = 0
    for tc, expected, message in test_cases:
        i += 1
        value, _ = has_valid_credentials(tc)
        if value != expected:
            raise ValueError(f"Error in test case {i}: {message}")
