from tko.config.app_settings import AppSettings
from tko.i18n import Msg, MsgRT, normalize_language, set_language, t, tr
from tko.util.rt import RT


_CLI_COMMON_NO_REPO = Msg(
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
        assert t(_CLI_COMMON_NO_REPO) == "No TKO repository found."
        set_language("pt-BR")
        assert t(_CLI_COMMON_NO_REPO) == "Nenhum repositório TKO encontrado."

    def test_string_fallback_uses_literal_template(self):
        set_language("en")
        assert t("No catalog {value}", value="path") == "No catalog path"

    def test_app_settings_ui_language_roundtrip(self):
        settings = AppSettings(ui_language="en")
        restored = AppSettings.from_dict(settings.to_dict())
        assert restored.ui_language == "en"

    def test_translate_rt_pt_and_en(self):
        msg = MsgRT(pt=RT("Ola", "g"), en=RT("Hello", "y"))
        set_language("en")
        assert tr(msg).plain() == "Hello"
        assert tr(msg).runs[0][0] == "y"

        set_language("pt-BR")
        assert tr(msg).plain() == "Ola"
        assert tr(msg).runs[0][0] == "g"
