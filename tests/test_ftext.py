# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest


from tko.util.ftext import Sentence, Token

class TestSimple(unittest.TestCase):
    def test_token_creation(self):
        token = Token("text1","g")
        assert token.text == "text1"
        assert token.fmt == "g"

    def test_getitem(self):
        sentence = Sentence() + Token("tex", "g") + Token("gu", "r")
        assert sentence[0] == Token("t", "g")
        assert sentence[1] == Token("e", "g")
        assert str(sentence[2]) == str(Token("x", "g"))
        assert sentence[2] == Token("x", "g")
        assert sentence[3] == Token("g", "r")
        assert sentence[4] == Token("u", "r")


    def test_token_addition(self):
        token1 = Token("text1", "g")
        token2 = Token("text2", "r")
        sentence = token1 + token2
        assert len(sentence) == 10
        assert sentence[0] == Token("t", "g")
        assert sentence.resume_val_fmt() == ("text1text2", "gggggrrrrr")

    def test_token_equality(self):
        token1 = Token("text1", "fmt1")
        token2 = Token("text1", "fmt1")
        token3 = Token("text2", "fmt2")
        assert token1 == token2
        assert token1 != token3

    def test_token_length(self):
        token = Token("text1", "fmt1")
        assert len(token) == 5

    def test_sentence_creation(self):
        sentence = Sentence()
        assert len(sentence) == 0

    def test_sentence_addition(self):
        sentence1 = Sentence() + Token("text1", "")
        sentence2 = Sentence() + Token("text2", "r")
        sentence3 = sentence1 + sentence2
        assert len(sentence3) == 10
        assert sentence3.resume_val_fmt() == ("text1text2", "     rrrrr")
        sentence4 = sentence1 + "text3"
        assert len(sentence4) == 10
        assert sentence4.resume_val_fmt() == ("text1text3", "          ")

    def test_sentence_equality(self):
        sentence1 = Sentence() + Token("text1", "fmt1") + Token("text2", "fmt2")
        sentence2 = Sentence() + Token("text1", "fmt1") + Token("text2", "fmt2")
        sentence3 = Sentence() + Token("text3", "fmt3")
        assert sentence1 == sentence2
        assert sentence1 != sentence3

    def test_sentence_len(self):
        sentence = Sentence() + Token("text1", "fmt1") + Token("text2", "fmt2")
        assert sentence.len() == 10

    def test_sentence_trim_end(self):
        sentence = Sentence() + Token("text1", "r") + Token("text2", "g")
        trimmed_sentence = sentence.trim_end(7)
        assert trimmed_sentence.len() == 7
        assert trimmed_sentence.resume_val_fmt() == ("text1te", "rrrrrgg")

    def test_build_bar(self):
        bar = Sentence.build_bar("loading", 0.5, 20, fmt_true="C", fmt_false="Y")
        assert bar.len() == 20
        assert str(bar) == str(Token("      load", 'C') + Token('ing       ', 'Y'))
        assert bar.resume_val_fmt() == ("      loading       ", "CCCCCCCCCCYYYYYYYYYY")

    def test_text_replace(self):
        bar = Sentence() + Token("text1foo", "g") + Token("text2", "b")
        bar.replace("t", Token("x", "r"))
        assert bar.resume_val_fmt() == ("xexx1fooxexx2", "rggrggggrbbrb")
        

# Execute os testes
if __name__ == "__main__":
    unittest.main()
