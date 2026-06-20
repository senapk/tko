from tko.i18n import Msg, normalize_language, set_language


_CLI_COMMON_NO_REPO = Msg.text(
    pt="Nenhum repositório TKO encontrado.",
    en="No TKO repository found.",
)


class TestI18N:
    def teardown_method(self):
        set_language("pt-BR")

    def test_normalize_language_aliases(self):
        assert normalize_language("pt") == "pt-BR"
        assert normalize_language("pt_BR") == "pt-BR"
        assert normalize_language("en_us") == "en"
        assert normalize_language("unknown") == "pt-BR"

    def test_translate_pt_and_en(self):
        set_language("en")
        assert str(_CLI_COMMON_NO_REPO) == "No TKO repository found."
        set_language("pt-BR")
        assert str(_CLI_COMMON_NO_REPO) == "Nenhum repositório TKO encontrado."

    def test_string_fallback_uses_literal_template(self):
        set_language("en")
        assert str("No catalog {value}").format(value="path") == "No catalog path"
