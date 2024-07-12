# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest


from tko.util.ftext import FF, TK
from icecream import ic

class TestSimple(unittest.TestCase):
    def test_token_creation(self):
        token = TK("text1","g")
        assert token.text == "text1"
        assert token.fmt == "g"

    def test_getitem(self):
        sentence = FF() + ("tex", "g") + ("gu", "r")
        assert sentence[0] == TK("t", "g")
        assert sentence[1] == TK("e", "g")
        assert str(sentence[2]) == str(TK("x", "g"))
        assert sentence[2] == TK("x", "g")
        assert sentence[3] == TK("g", "r")
        assert sentence[4] == TK("u", "r")


    def test_token_addition(self):
        token1 = TK("text1", "g")
        token2 = TK("text2", "r")
        sentence = token1 + token2
        assert len(sentence) == 10
        assert sentence[0] == TK("t", "g")
        assert sentence.resume_val_fmt() == ("text1text2", "gggggrrrrr")

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
        sentence1 = FF() + ("text1", "")
        sentence2 = FF() + ("text2", "r")
        sentence3 = sentence1 + sentence2
        assert len(sentence3) == 10
        assert sentence3.resume_val_fmt() == ("text1text2", "     rrrrr")
        sentence4 = sentence1 + "text3"
        assert len(sentence4) == 10
        assert sentence4.resume_val_fmt() == ("text1text3", "          ")

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
        sentence = FF() + ("text1", "r") + ("text2", "g")
        trimmed_sentence = sentence.trim_end(7)
        assert trimmed_sentence.len() == 7
        assert trimmed_sentence.resume_val_fmt() == ("text1te", "rrrrrgg")

    def test_build_bar(self):
        bar = FF.build_bar("loading", 0.5, 20, fmt_true="C", fmt_false="Y")
        assert bar.len() == 20
        assert str(bar) == str(TK("      load", 'C') + TK('ing       ', 'Y'))
        assert bar.resume_val_fmt() == ("      loading       ", "CCCCCCCCCCYYYYYYYYYY")

    def test_text_replace(self):
        bar = FF() + ("text1foo", "g") + ("text2", "b")
        bar.replace("t", TK("x", "r"))
        assert bar.resume_val_fmt() == ("xexx1fooxexx2", "rggrggggrbbrb")
        

# Execute os testes
if __name__ == "__main__":
    unittest.main()
