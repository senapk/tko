# # the inclusion of the tests module is not meant to offer best practices for
# # testing in general, but rather to support the `find_packages` example in
# # setup.py that excludes installing the "tests" package

# import unittest

# from tko.util.ftext import FF
# from tko.run.diff import Diff
# from tko.util.symbols import symbols
# from tko.util.term_color import term_print


# class TestSimple(unittest.TestCase):

#     def test_arrow_up(self):
#         a = FF() + "banana"
#         b = FF() + "baralho"
#         c = Diff.make_line_arrow_up(a, b).join()
#         d = FF().add("  ").add(symbols.arrow_up).join()
        
#         assert str(c) == str(d)

#     def test_render_white(self):
#         a = FF() + "banana eh gostosa  demais "
#         b = Diff.render_white(a).join()
#         w = symbols.whitespace.text
#         c = FF() + "banana eh gostosa  demais ".replace(' ', w)
#         assert str(b) == str(c)

#     def test_render_white2(self):
#         a = FF() + "banana eh gostosa  demais "
#         b = Diff.render_white(a, "r").join()
#         w = symbols.whitespace.text
#         c = FF() + ('banana', '') + ('⸱', 'r') + ('eh', '') + ('⸱', 'r') + ('gostosa', '') + ('⸱⸱', 'r') + ('demais', '') + ('⸱', 'r')
#         assert str(b) == str(c)

#     def test_find_first_missmatch(self):
#         a = FF() + "banana eh gostosa  demais "
#         b = FF() + "banana eh gostoso demais"
#         c = Diff.find_first_mismatch(a, b)
#         assert c == 16

#     def test_colorize_2_lines_diff(self):
#         a = FF() + "banana eh gostosa demais"
#         b = FF() + "banana eh gostoso demais"
#         c, d = Diff.colorize_2_lines_diff(a, b)
#         c1 = FF().add("banana eh gostos").addf("g", "a demais")
#         d1 = FF().add("banana eh gostos").addf("r", "o demais")
#         assert str(c1) == str(c)
#         assert c1 == c
#         assert d1 == d

# if __name__ == '__main__':
#     unittest.main()
