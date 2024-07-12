# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest


from tko.util.ftext import FF, TK

class TestSimple(unittest.TestCase):
    def test_token_creation(self):
        token = TK("text1","fmt1")
        assert token.fmt == "fmt1"
        assert token.text == "text1"

    def test_getitem(self):
        sentence = FF() + ("tex", "fmt1") + ("gu", "fmt2")
        assert sentence[0] == TK("t", "fmt1")
        assert sentence[1] == TK("e", "fmt1")
        assert str(sentence[2]) == str(TK("x", "fmt1"))
        assert sentence[2] == TK("x", "fmt1")
        assert sentence[3] == TK("g", "fmt2")
        assert sentence[4] == TK("u", "fmt2")
        assert sentence[5] == TK()



    def test_token_addition(self):
        token1 = TK("text1", "fmt1")
        token2 = TK("text2", "fmt2")
        sentence = token1 + token2
        assert len(sentence) == 10
        assert sentence.get(0).text == "text1"
        assert sentence.get(0) == token1
        assert sentence.get(1) == token2

        sentence = token1 + "text3"
        assert len(sentence) == 10
        assert sentence.get(0) == token1
        assert sentence.get(1).text == "text3"

    def test_token_equality(self):
        token1 = TK("text1", "fmt1")
        token2 = TK("text1", "fmt1")
        token3 = TK("text2", "fmt2")
        assert token1 == token2
        assert token1 != token3

    def test_token_length(self):
        token = TK("text1", "fmt1")
        assert len(token) == 5

    def test_sentence_creation(self):
        sentence = FF()
        assert len(sentence) == 0

    def test_sentence_addition(self):
        sentence1 = FF() + ("text1", "fmt1")
        sentence2 = FF() + ("text2", "fmt2")
        sentence3 = sentence1 + sentence2
        assert len(sentence3) == 10
        assert sentence3.get(0).text == "text1"
        assert sentence3.get(1).text == "text2"

        sentence4 = sentence1 + "text3"
        assert len(sentence4) == 10
        assert sentence4.get(0).text == "text1"
        assert sentence4.get(1).text == "text3"

    def test_sentence_equality(self):
        sentence1 = FF() + ("text1", "fmt1") + ("text2", "fmt2")
        sentence2 = FF() + ("text1", "fmt1") + ("text2", "fmt2")
        sentence3 = FF() + ("text3", "fmt3")
        assert sentence1 == sentence2
        assert sentence1 != sentence3

    def test_sentence_len(self):
        sentence = FF() + ("text1", "fmt1") + ("text2", "fmt2")
        assert sentence.len() == 10

    def test_sentence_trim_end(self):
        sentence = FF() + ("text1", "fmt1") + ("text2", "fmt2")
        trimmed_sentence = sentence.trim_end(7)
        assert trimmed_sentence.len() == 7
        assert trimmed_sentence.get(1).text == "te"

    def test_build_bar(self):
        bar = FF.build_bar("loading", 0.5, 20, fmt_true="/kC", fmt_false="/kY")
        assert bar.len() == 20
        assert bar.get(0).fmt == "/kC"
        assert bar.get(-1).fmt == "/kY"

    def test_text_replace(self):
        bar = FF() + ("text1foo", "g") + ("text2", "b")
        bar.replace("t", TK("x", "r"))
        expected = FF() + ("x", "r") + ("ex", "g") + ("x", "r") + ("1foo", "g") + ("x", "r") + ("ex", "b") + ("x", "r") + ("2", "b")
        assert str(bar) == str(expected)

# Execute os testes
if __name__ == "__main__":
    unittest.main()
