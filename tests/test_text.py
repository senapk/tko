# the inclusion of the tests module is not meant to offer best practices for
# testing in general, but rather to support the `find_packages` example in
# setup.py that excludes installing the "tests" package


from tko.util.text  import Text

class TestSimple:
    def test_token_creation(self):
        token: Text.Token = Text.Token("text1","g")
        assert token.text == "text1"
        assert token.fmt == "g"

    def test_getitem(self):
        sentence = Text() + Text.Token("tex", "g") + Text.Token("gu", "r")
        assert sentence[0] == Text.Token("t", "g")
        assert sentence[1] == Text.Token("e", "g")
        assert str(sentence[2]) == str(Text.Token("x", "g"))
        assert sentence[2] == Text.Token("x", "g")
        assert sentence[3] == Text.Token("g", "r")
        assert sentence[4] == Text.Token("u", "r")


    def test_token_addition(self):
        token1 = Text.Token("text1", "g")
        token2 = Text.Token("text2", "r")
        sentence = token1 + token2
        assert len(sentence) == 10
        assert sentence[0] == Text.Token("t", "g")
        assert "".join([x.fmt for x in sentence.get_data()]) == "gggggrrrrr"
        assert "".join([x.text for x in sentence.get_data()]) == "text1text2"

    def test_token_equality(self):
        token1 = Text.Token("text1", "fmt1")
        token2 = Text.Token("text1", "fmt1")
        token3 = Text.Token("text2", "fmt2")
        assert token1 == token2
        assert token1 != token3

    def test_token_length(self):
        token = Text.Token("text1", "fmt1")
        assert len(token) == 5

    def test_sentence_creation(self):
        sentence = Text()
        assert len(sentence) == 0

    def test_sentence_addition(self):
        sentence1 = Text() + Text.Token("text1", "")
        sentence2 = Text() + Text.Token("text2", "r")
        sentence3 = sentence1 + sentence2
        assert len(sentence3) == 10
        assert "".join([x.fmt for x in sentence3.get_data()]) == "rrrrr"
        assert "".join([x.text for x in sentence3.get_data()]) == "text1text2"
        assert sentence3.resume() == [Text.Token("text1"), Text.Token("text2", "r")]
        sentence4 = sentence1 + "text3"
        assert len(sentence4) == 10
        assert sentence4.resume() == [Text.Token("text1text3")]

    def test_sentence_equality(self):
        sentence1 = Text() + Text.Token("text1", "fmt1") + Text.Token("text2", "fmt2")
        sentence2 = Text() + Text.Token("text1", "fmt1") + Text.Token("text2", "fmt2")
        sentence3 = Text() + Text.Token("text3", "fmt3")
        assert sentence1 == sentence2
        assert sentence1 != sentence3

    def test_sentence_len(self):
        sentence = Text() + Text.Token("text1", "fmt1") + Text.Token("text2", "fmt2")
        assert sentence.len() == 10

    def test_sentence_trim_end(self):
        sentence = Text() + Text.Token("text1", "r") + Text.Token("text2", "g")
        trimmed_sentence = sentence.trim_end(7)
        assert trimmed_sentence.len() == 7
        assert trimmed_sentence.resume() == [Text.Token("text1", "r"), Text.Token("te", "g")]

    def test_text_replace1(self):
        bar = Text() + Text.Token("text1foo", "g") + Text.Token("text2", "b")
        bar.replace("t", Text.Token("x", "r"))
        assert "".join([x.text for x in bar.get_data()]) == "xexx1fooxexx2"
        assert "".join([x.fmt for x in bar.get_data()]) == "rggrggggrbbrb"

    def test_text_replace2(self):
        bar = Text.format("123456789")
        bar.replace("123", Text.Token("abc", "r"))
        assert str(bar) == str(Text.format("{r}456789", "abc"))

        bar = Text.format("123456789")
        bar.replace("123", Text.Token("ab", "r"))
        assert str(bar) == str(Text.format("{r}456789", "ab"))

        bar = Text.format("0123412789")
        bar.replace("12", Text.Token("a", "r"))
        assert str(bar) == str(Text.format("0{r}34{r}789", "a", "a"))

        bar = Text.format("0123412789")
        bar.replace("12", Text.Token("abcd", "r"))
        assert str(bar) == str(Text.format("0{r}34{r}789", "abcd", "abcd"))


    def test_resume1(self):
        sentence = Text() + Text.Token("text1", "g") + Text.Token("text2", "g")
        assert sentence.resume() == [Text.Token("text1text2", "g")]

    def test_resume2(self):
        sentence = Text() + Text.Token("text1", "g") + Text.Token("text2", "r")
        assert sentence.resume() == [Text.Token("text1", "g"), Text.Token("text2", "r")]
    

    def test_split_1(self):
        sentence = Text() + Text.Token("text1", "g") + Text.Token("ext2", "r")
        assert sentence.split("t") == [Text(), Text().addf("g", "ex"), Text().addf("g", "1").addf("r", "ex"), Text().addf("r", "2")]

    def test_slice(self):
        sentence = Text() + Text.Token("text1", "g") + Text.Token("text2", "r")
        assert sentence.slice(1, -1) == Text().addf("g", "ext1") + Text.Token("text", "r")
        print(sentence.slice(1, -1))
        assert sentence.slice(1) == Text().addf("g", "ext1") + Text.Token("text2", "r")
        assert sentence.slice() == Text().addf("g", "text1") + Text.Token("text2", "r")

    def test_format(self):
        text1 = Text.format("brasil é {g} e {y}", "verde", "amarelo")
        text2 = Text.format("brasil é ").addf("g", "verde").add(" e ").addf("y", "amarelo")
        assert str(text1) == str(text2)

        text1 = Text.format("ceu é {b}, ouro é {}", "azul", Text.Token("amarelo", "y"))
        text2 = Text().add("ceu é ").addf("b", "azul").add(", ouro é ").addf("y", "amarelo")
        assert str(text1) == str(text2)

        text1 = Text.format("sangue é {}, mar é {c}", Text.format("{r}", "vermelho"), Text.Token("ciano", "r"))
        text2 = Text().add("sangue é ").addf("r", "vermelho").add(", mar é ").addf("c", "ciano")
        assert str(text1) == str(text2)

    def test_format_default(self):
        text1 = Text("b").add("banana").add(Text.Token("uva", "g")).add(Text("r").add("ovo"))
        assert text1.resume() == [Text.Token("banana", "b"), Text.Token("uva", "g"), Text.Token("ovo", "r")]

    def test_format_default2(self):
        text1 = Text("b") + "banana" + " " + "madura"
        text2 = Text("b").add("banana").add(" ").add("madura")
        assert str(text1) == str(text2)
        assert text1.resume() == [Text.Token("banana madura", "b")]
        text1 = Text("b") + "banana" + Text("r") + Text.Token("madura", "g")
        assert text1.resume() == [Text.Token("banana", "b"), Text.Token("madura", "g")]

    def test_format_1(self):
        text1 = Text.format("brasil é {g} e {y}", "verde", "amarelo", " e azul")
        text2 = Text().add("brasil é ").addf("g", "verde").add(" e ").addf("y", "amarelo").add(" e azul")
        assert str(text1) == str(text2)

        text3 = Text.format("o brasil é {g:verde} e {y:amarelo}.")
        text4 = Text.format("o brasil é {} e {}.", Text.Token("verde", "g"), Text.Token("amarelo", "y"))
        assert str(text3) == str(text4)

        text5 = Text() + "o brasil é " + Text("g") + "verde" + Text() + " e " + Text("y") + "amarelo"
        assert text5.resume() == [Text.Token("o brasil é "), Text.Token("verde", "g"), Text.Token(" e "), Text.Token("amarelo", "y")]

    def test_tuple(self):
        text1 = Text().addf("g", "brasil").add(" é ").addf("r", "lindo")
        print(text1)
        print("chiclete")
