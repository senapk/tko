import csv

class CSV:
    quest_char = '='
    @staticmethod
    def format_sheet(sheet: list[list[str]]) -> list[list[str]]:
        nl = len(sheet)
        nc = len(sheet[0])

        for c in range(nc):
            for l in range(nl):
                sheet[l][c] = sheet[l][c].strip()

        for c in range(nc):
            max_len = 0
            for l in range(nl):
                max_len = max(max_len, len(sheet[l][c]))
            for l in range(nl):
                fillchar = ' ' if sheet[l][c][0] != CSV.quest_char else CSV.quest_char
                if c == 0:
                    if fillchar == CSV.quest_char:
                        sheet[l][c] = sheet[l][c].ljust(max_len, fillchar)
                    else:
                        sheet[l][c] = sheet[l][c].ljust(max_len, fillchar)
                else:
                    sheet[l][c] = sheet[l][c].rjust(max_len, fillchar)
        return sheet
    
    @staticmethod
    def load_csv(arquivo_csv: str) -> list[list[str]]:
        try:
            with open(arquivo_csv, "r", newline="", encoding="utf-8") as csvfile:
                reader = csv.reader(csvfile)
                sheet = list(reader)
                return sheet
        except FileNotFoundError:
            exit(f"Arquivo '{arquivo_csv}' não encontrado.")

    @staticmethod
    def save_csv(arquivo_csv: str, sheet: list[list[str]]):
        try:
            with open(arquivo_csv, "w", newline="", encoding="utf-8") as csvfile:
                writer = csv.writer(csvfile)
                writer.writerows(sheet)
        except FileNotFoundError:
            exit(f"Arquivo '{arquivo_csv}' não encontrado.")