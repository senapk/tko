# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest


from tko.util.ftext import Ftext, Token

class TestSimple(unittest.TestCase):
    def test_token_creation(self):
        token = Token("fmt1", "text1")
        assert token.fmt == "fmt1"
        assert token.text == "text1"

    def test_token_addition(self):
        token1 = Token("fmt1", "text1")
        token2 = Token("fmt2", "text2")
        sentence = token1 + token2
        assert len(sentence) == 10
        assert sentence[0].text == "text1"
        assert sentence[0] == token1
        assert sentence[1] == token2

        sentence = token1 + "text3"
        assert len(sentence) == 10
        assert sentence[0] == token1
        assert sentence[1].text == "text3"

    def test_token_equality(self):
        token1 = Token("fmt1", "text1")
        token2 = Token("fmt1", "text1")
        token3 = Token("fmt2", "text2")
        assert token1 == token2
        assert token1 != token3

    def test_token_length(self):
        token = Token("fmt1", "text1")
        assert len(token) == 5

    def test_sentence_creation(self):
        sentence = Ftext()
        assert len(sentence) == 0

    def test_sentence_addition(self):
        sentence1 = Ftext() + ("fmt1", "text1")
        sentence2 = Ftext() + ("fmt2", "text2")
        sentence3 = sentence1 + sentence2
        assert len(sentence3) == 10
        assert sentence3[0].text == "text1"
        assert sentence3[1].text == "text2"

        sentence4 = sentence1 + "text3"
        assert len(sentence4) == 10
        assert sentence4[0].text == "text1"
        assert sentence4[1].text == "text3"

    def test_sentence_equality(self):
        sentence1 = Ftext() + ("fmt1", "text1") + ("fmt2", "text2")
        sentence2 = Ftext() + ("fmt1", "text1") + ("fmt2", "text2")
        sentence3 = Ftext() + ("fmt3", "text3")
        assert sentence1 == sentence2
        assert sentence1 != sentence3

    def test_sentence_len(self):
        sentence = Ftext() + ("fmt1", "text1") + ("fmt2", "text2")
        assert sentence.len() == 10

    def test_sentence_trim_end(self):
        sentence = Ftext() + ("fmt1", "text1") + ("fmt2", "text2")
        trimmed_sentence = sentence.trim_end(7)
        assert trimmed_sentence.len() == 7
        assert trimmed_sentence[1].text == "te"

    def test_build_bar(self):
        bar = Ftext.build_bar("loading", 0.5, 20, fmt_true="/kC", fmt_false="/kY")
        assert bar.len() == 20
        assert bar[0].fmt == "/kC"
        assert bar[-1].fmt == "/kY"

# Execute os testes
if __name__ == "__main__":
    unittest.main()
