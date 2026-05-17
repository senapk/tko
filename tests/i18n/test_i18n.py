from tko.config.app_settings import AppSettings
from tko.i18n import MsgKey, get_catalog_keys, normalize_language, set_language, t


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
        assert t(MsgKey.RESET_NO_REPO) == "No TKO repository found."
        set_language("pt-BR")
        assert t(MsgKey.RESET_NO_REPO) == "Nenhum repositório TKO encontrado."

    def test_msg_key_matches_catalogs(self):
        keys = {key.value for key in MsgKey}
        assert keys == get_catalog_keys("pt-BR")
        assert keys == get_catalog_keys("en")

    def test_app_settings_ui_language_roundtrip(self):
        settings = AppSettings(ui_language="en")
        restored = AppSettings.from_dict(settings.to_dict())
        assert restored.ui_language == "en"
