# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package

import unittest


from tko.util.text import Text, Token

class TestSimple(unittest.TestCase):
    def test_token_creation(self):
        token = Token("text1","g")
        assert token.text == "text1"
        assert token.fmt == "g"

    def test_getitem(self):
        sentence = Text() + Token("tex", "g") + Token("gu", "r")
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
        assert "".join([x.fmt for x in sentence.get_data()]) == "gggggrrrrr"
        assert "".join([x.text for x in sentence.get_data()]) == "text1text2"

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
        sentence = Text()
        assert len(sentence) == 0

    def test_sentence_addition(self):
        sentence1 = Text() + Token("text1", "")
        sentence2 = Text() + Token("text2", "r")
        sentence3 = sentence1 + sentence2
        assert len(sentence3) == 10
        assert "".join([x.fmt for x in sentence3.get_data()]) == "rrrrr"
        assert "".join([x.text for x in sentence3.get_data()]) == "text1text2"
        assert sentence3.resume() == [Token("text1"), Token("text2", "r")]
        sentence4 = sentence1 + "text3"
        assert len(sentence4) == 10
        assert sentence4.resume() == [Token("text1text3")]

    def test_sentence_equality(self):
        sentence1 = Text() + Token("text1", "fmt1") + Token("text2", "fmt2")
        sentence2 = Text() + Token("text1", "fmt1") + Token("text2", "fmt2")
        sentence3 = Text() + Token("text3", "fmt3")
        assert sentence1 == sentence2
        assert sentence1 != sentence3

    def test_sentence_len(self):
        sentence = Text() + Token("text1", "fmt1") + Token("text2", "fmt2")
        assert sentence.len() == 10

    def test_sentence_trim_end(self):
        sentence = Text() + Token("text1", "r") + Token("text2", "g")
        trimmed_sentence = sentence.trim_end(7)
        assert trimmed_sentence.len() == 7
        assert trimmed_sentence.resume() == [Token("text1", "r"), Token("te", "g")]

    def test_text_replace1(self):
        bar = Text() + Token("text1foo", "g") + Token("text2", "b")
        bar.replace("t", Token("x", "r"))
        assert "".join([x.text for x in bar.get_data()]) == "xexx1fooxexx2"
        assert "".join([x.fmt for x in bar.get_data()]) == "rggrggggrbbrb"

    def test_text_replace2(self):
        bar = Text("123456789")
        bar.replace("123", Token("abc", "r"))
        assert str(bar) == str(Text("{r}456789", "abc"))

        bar = Text("123456789")
        bar.replace("123", Token("ab", "r"))
        assert str(bar) == str(Text("{r}456789", "ab"))

        bar = Text("0123412789")
        bar.replace("12", Token("a", "r"))
        assert str(bar) == str(Text("0{r}34{r}789", "a", "a"))

        bar = Text("0123412789")
        bar.replace("12", Token("abcd", "r"))
        assert str(bar) == str(Text("0{r}34{r}789", "abcd", "abcd"))


    def test_resume1(self):
        sentence = Text() + Token("text1", "g") + Token("text2", "g")
        assert sentence.resume() == [Token("text1text2", "g")]

    def test_resume2(self):
        sentence = Text() + Token("text1", "g") + Token("text2", "r")
        assert sentence.resume() == [Token("text1", "g"), Token("text2", "r")]
    

    def test_split_1(self):
        sentence = Text() + Token("text1", "g") + Token("ext2", "r")
        assert sentence.split("t") == [Text(), Text().addf("g", "ex"), Text().addf("g", "1").addf("r", "ex"), Text().addf("r", "2")]

    def test_slice(self):
        sentence = Text() + Token("text1", "g") + Token("text2", "r")
        assert sentence.slice(1, -1) == Text().addf("g", "ext1") + Token("text", "r")
        print(sentence.slice(1, -1))
        assert sentence.slice(1) == Text().addf("g", "ext1") + Token("text2", "r")
        assert sentence.slice() == Text().addf("g", "text1") + Token("text2", "r")

    def test_format(self):
        text1 = Text("brasil é {g} e {y}", "verde", "amarelo")
        text2 = Text("brasil é ").addf("g", "verde").add(" e ").addf("y", "amarelo")
        assert str(text1) == str(text2)

        text1 = Text("ceu é {b}, ouro é {}", "azul", Token("amarelo", "y"))
        text2 = Text().add("ceu é ").addf("b", "azul").add(", ouro é ").addf("y", "amarelo")
        assert str(text1) == str(text2)

        text1 = Text("sangue é {}, mar é {c}", Text("{r}", "vermelho"), Token("ciano", "r"))
        text2 = Text().add("sangue é ").addf("r", "vermelho").add(", mar é ").addf("c", "ciano")
        assert str(text1) == str(text2)

if __name__ == "__main__":
    unittest.main()
