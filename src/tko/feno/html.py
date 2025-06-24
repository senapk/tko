import argparse
import markdown
from typing import Any
from tko.feno.title import FenoTitle

def convert_lists_to_4_spaces(markdown_content: str) -> str:
    """
    Converte listas no conteúdo Markdown para usar 4 espaços como indentação.

    Args:
        markdown_content (str): O conteúdo Markdown a ser processado.

    Returns:
        str: O conteúdo Markdown com listas convertidas para 4 espaços.
    """
    lines = markdown_content.splitlines()
    output_lines: list[str] = []
    for line in lines:
        lstrip = line.lstrip()
        if lstrip.startswith('- '):
            dif = len(line) - len(lstrip)
            line = ' ' * (2 * dif) + lstrip
        output_lines.append(line)
    return '\n'.join(output_lines)

def convert_markdown_to_html(title: str, markdown_file_path: str, output_html_path: str):
    try:
        with open(markdown_file_path, 'r', encoding='utf-8') as f:
            markdown_content = f.read()
        markdown_content = convert_lists_to_4_spaces(markdown_content)

        # Configura as extensões do Markdown
        # 'tables': para renderizar tabelas
        # 'fenced_code': para blocos de código com destaque de sintaxe
        # 'pymdownx.arithmatex': para renderizar LaTeX (necessita MathJax ou KaTeX no HTML)
        # 'pymdownx.highlight': para o destaque de sintaxe (depende de pygments)
        extensions = [
            'tables',
            "pymdownx.superfences",
            'pymdownx.arithmatex', # Usando arithmatex para LaTeX
            'pymdownx.highlight',  # Usando highlight para destaque de sintaxe
            'attr_list',           # Útil para atributos como classes em elementos
        ]
        extension_configs: dict[str, Any] = {
            'pymdownx.arithmatex': {
                'generic': True  # Habilita delimitadores genéricos para LaTeX ($...$ e $$...$$)
            },
            'pymdownx.highlight': {
                'css_class': 'highlight', # Classe CSS para os blocos de código
                'linenums': False,       # Não mostrar números de linha por padrão
                'pygments_lang_class': True, # Adiciona classes de linguagem para Pygments
            }
        }

        html_content = markdown.markdown(
            markdown_content,
            extensions=extensions,
            extension_configs=extension_configs
        )

        # Adiciona um CSS básico e o script do MathJax para o LaTeX
        final_html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <style>
        body {{ font-family: sans-serif; line-height: 1.6; margin: 20px; }}
        pre {{ background-color: #f4f4f4; padding: 10px; border-radius: 5px; overflow-x: auto; }}
        code {{ font-family: monospace; }}
        table {{ border-collapse: collapse; width: 100%; }}
        th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
        th {{ background-color: #f2f2f2; }}
        /* Estilos básicos para o destaque de sintaxe (gerado pelo pygments via pymdownx.highlight) */
        .highlight .hll {{ background-color: #ffffcc }}
        .highlight .c {{ color: #999988; font-style: italic }} /* Comment */
        .highlight .err {{ color: #a61717; background-color: #e3d2d2 }} /* Error */
        .highlight .k {{ color: #000000; font-weight: bold }} /* Keyword */
        .highlight .o {{ color: #000000; font-weight: bold }} /* Operator */
        .highlight .ch {{ color: #999988; font-style: italic }} /* Comment.Hashbang */
        .highlight .cm {{ color: #999988; font-style: italic }} /* Comment.Multiline */
        .highlight .cp {{ color: #999999; font-weight: bold; font-style: italic }} /* Comment.Preproc */
        .highlight .cpf {{ color: #999988; font-style: italic }} /* Comment.PreprocFile */
        .highlight .c1 {{ color: #999988; font-style: italic }} /* Comment.Single */
        .highlight .cs {{ color: #999999; font-weight: bold; font-style: italic }} /* Comment.Special */
        .highlight .gd {{ color: #000000; background-color: #ffdddd }} /* Generic.Deleted */
        .highlight .ge {{ color: #000000; font-style: italic }} /* Generic.Emph */
        .highlight .gr {{ color: #aa0000 }} /* Generic.Error */
        .highlight .gh {{ color: #999999 }} /* Generic.Heading */
        .highlight .gi {{ color: #000000; background-color: #ddffdd }} /* Generic.Inserted */
        .highlight .go {{ color: #888888 }} /* Generic.Output */
        .highlight .gp {{ color: #555555 }} /* Generic.Prompt */
        .highlight .gs {{ font-weight: bold }} /* Generic.Strong */
        .highlight .gu {{ color: #aaaaaa }} /* Generic.Subheading */
        .highlight .gt {{ color: #aa0000 }} /* Generic.Traceback */
        .highlight .kc {{ color: #000000; font-weight: bold }} /* Keyword.Constant */
        .highlight .kd {{ color: #000000; font-weight: bold }} /* Keyword.Declaration */
        .highlight .kn {{ color: #000000; font-weight: bold }} /* Keyword.Namespace */
        .highlight .kp {{ color: #000000; font-weight: bold }} /* Keyword.Pseudo */
        .highlight .kr {{ color: #000000; font-weight: bold }} /* Keyword.Reserved */
        .highlight .kt {{ color: #445588; font-weight: bold }} /* Keyword.Type */
        .highlight .m {{ color: #009999 }} /* Literal.Number */
        .highlight .s {{ color: #dd1144 }} /* Literal.String */
        .highlight .na {{ color: #008080 }} /* Name.Attribute */
        .highlight .nb {{ color: #0086B3 }} /* Name.Builtin */
        .highlight .nc {{ color: #445588; font-weight: bold }} /* Name.Class */
        .highlight .no {{ color: #008080 }} /* Name.Constant */
        .highlight .nd {{ color: #3c5d5d; font-weight: bold }} /* Name.Decorator */
        .highlight .ni {{ color: #800080 }} /* Name.Entity */
        .highlight .ne {{ color: #990000; font-weight: bold }} /* Name.Exception */
        .highlight .nf {{ color: #990000; font-weight: bold }} /* Name.Function */
        .highlight .nl {{ color: #990000; font-weight: bold }} /* Name.Label */
        .highlight .nn {{ color: #555555; font-weight: bold }} /* Name.Namespace */
        .highlight .nx {{ color: #990000; font-weight: bold }} /* Name.Other */
        .highlight .py {{ color: #009999 }} /* Name.Property */
        .highlight .p {{ color: #000000 }} /* Name.Punctuation */
        .highlight .nv {{ color: #008080 }} /* Name.Variable */
        .highlight .ow {{ color: #000000; font-weight: bold }} /* Operator.Word */
        .highlight .w {{ color: #bbbbbb }} /* Text.Whitespace */
        .highlight .mf {{ color: #009999 }} /* Literal.Number.Float */
        .highlight .mh {{ color: #009999 }} /* Literal.Number.Hex */
        .highlight .mi {{ color: #009999 }} /* Literal.Number.Integer */
        .highlight .mo {{ color: #009999 }} /* Literal.Number.Oct */
        .highlight .sb {{ color: #dd1144 }} /* Literal.String.Backtick */
        .highlight .sc {{ color: #dd1144 }} /* Literal.String.Char */
        .highlight .sd {{ color: #dd1144 }} /* Literal.String.Doc */
        .highlight .s2 {{ color: #dd1144 }} /* Literal.String.Double */
        .highlight .se {{ color: #dd1144 }} /* Literal.String.Escape */
        .highlight .sh {{ color: #dd1144 }} /* Literal.String.Heredoc */
        .highlight .si {{ color: #dd1144 }} /* Literal.String.Interpol */
        .highlight .sx {{ color: #dd1144 }} /* Literal.String.Other */
        .highlight .sr {{ color: #009926 }} /* Literal.String.Regex */
        .highlight .s1 {{ color: #dd1144 }} /* Literal.String.Single */
        .highlight .ss {{ color: #dd1144 }} /* Literal.String.Symbol */
        .highlight .bp {{ color: #0086B3 }} /* Name.Builtin.Pseudo */
        .highlight .vc {{ color: #008080 }} /* Name.Variable.Class */
        .highlight .vg {{ color: #008080 }} /* Name.Variable.Global */
        .highlight .vi {{ color: #008080 }} /* Name.Variable.Instance */
        .highlight .il {{ color: #009999 }} /* Literal.Number.Integer.Long */
    </style>
    <script type="text/javascript" async
      src="https://cdnjs.cloudflare.com/ajax/libs/mathjax/2.7.7/MathJax.js?config=TeX-MML-AM_CHTML">
    </script>
</head>
<body>
{html_content}
</body>
</html>
"""

        with open(output_html_path, 'w', encoding='utf-8') as f:
            f.write(final_html)

        # print(f"Conversão concluída: '{markdown_file_path}' -> '{output_html_path}'")

    except FileNotFoundError:
        print(f"Erro: Arquivo Markdown não encontrado em '{markdown_file_path}'")
    except Exception as e:
        print(f"Ocorreu um erro durante a conversão: {e}")

def html_main(args: argparse.Namespace):
    # Verifica se os arquivos têm as extensões corretas
    if not args.input.endswith('.md'):
        print("Erro: O arquivo de entrada Markdown deve ter a extensão .md")
        exit(1)
    if not args.output.endswith('.html'):
        print("Erro: O arquivo de saída HTML deve ter a extensão .html")
        exit(1)

    title: str = ""
    if args.title:
        title = args.title
    else:
        title = FenoTitle.extract_title(args.input)
        
    convert_markdown_to_html(title, args.input, args.output)
