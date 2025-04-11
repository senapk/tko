import subprocess
from subprocess import PIPE
import tempfile
import argparse
import markdown
from tko.util.decoder import Decoder

class CssStyle:
    data = "body,li{color:#000}body{line-height:1.4em;max-width:42em;padding:1em;margin:auto}li{margin:.2em 0 0;padding:0}h1,h2,h3,h4,h5,h6{border:0!important}h1,h2{margin-top:.5em;margin-bottom:.5em;border-bottom:2px solid navy!important}h2{margin-top:1em}code,pre{border-radius:3px}pre{overflow:auto;background-color:#f8f8f8;border:1px solid #2f6fab;padding:5px}pre code{background-color:inherit;border:0;padding:0}code{background-color:#ffffe0;border:1px solid orange;padding:0 .2em}a{text-decoration:underline}ol,ul{padding-left:30px}em{color:#b05000}table.text td,table.text th{vertical-align:top;border-top:1px solid #ccc;padding:5px}"
    path = None
    @staticmethod
    def get_file():
        if CssStyle.path is None:
            CssStyle.path = tempfile.mktemp(suffix=".css")
            Decoder.save(CssStyle.path, CssStyle.data)
        return CssStyle.path
    
class HTML:

    @staticmethod
    def remove_css_link_from_html(html_file: str):
        content = Decoder.load(html_file)
        output = []
        for line in content.splitlines():
            if not line.startswith('  <link rel="stylesheet"'):
                output.append(line)
        Decoder.save(html_file, "\n".join(output))



    @staticmethod
    def pandoc_markdown_to_html(title: str, input_file: str, output_file: str, enable_latex: bool = True):
        fulltitle = title.replace('!', '\\!').replace('?', '\\?')
        cmd = ["pandoc", input_file, '--css', CssStyle.get_file(), '--metadata', 'pagetitle=' + fulltitle,
            '-s', '-o', output_file]
        if enable_latex:
            cmd.append("--mathjax")
        try:
            p = subprocess.Popen(cmd, stdout=PIPE, stderr=PIPE, universal_newlines=True)
            stdout, stderr = p.communicate()
            if stdout != "" or stderr != "":
                print(stdout)
                print(stderr)
            HTML.remove_css_link_from_html(output_file)

        except Exception as e:
            print("Erro no comando pandoc:", e)
            exit(1)


    @staticmethod
    def python_markdown_to_html(title: str, input_file_md: str, output_file_html: str):
        # Extensões mais comuns para melhorar a conversão
        extensions = ['extra', 'codehilite', 'toc']

        # Ler o conteúdo do arquivo markdown

        md_content = Decoder.load(input_file_md)

        # Converter markdown para HTML com as extensões
        html_content = markdown.markdown(md_content, extensions=extensions)

        # Criar estrutura básica de HTML com título
        html_template = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/styles/default.min.css">
        </head>
        <body>
            <h1>{title}</h1>
            {html_content}
            <script src="https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.7.0/highlight.min.js"></script>
            <script>hljs.highlightAll();</script>
        </body>
        </html>
        """

        # Escrever o HTML gerado no arquivo de saída
        Decoder.save(output_file_html, html_template)

        print(f'Arquivo HTML gerado em: {output_file_html}')


def html_main(args):
    HTML.pandoc_markdown_to_html(args.title, args.input, args.output, not args.no_latex)
