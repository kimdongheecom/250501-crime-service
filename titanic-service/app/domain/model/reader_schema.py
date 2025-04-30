from dataclasses import dataclass
import pandas as pd
import json

@dataclass
class ReaderSchema:
    _context: str = 'C://Users//bitcamp//Documents//kpmg-250424//kpmg2501//V2//ai-server//app//stored_data//crime'
    _fname: str = ''

    @property
    def context(self) -> str:
        return self._context

    @context.setter
    def context(self, context: str):
        self._context = context

    @property
    def fname(self) -> str:
        return self._fname

    @fname.setter
    def fname(self, fname: str):
        self._fname = fname

    def new_file(self) -> str:
        return f"{self._context}/{self._fname}"

    def csv_to_dframe(self) -> pd.DataFrame:
        file = self.new_file()
        return pd.read_csv(file, thousands=',')

    def xls_to_dframe(self, header=0, usecols=None) -> pd.DataFrame:
        file = self.new_file()
        return pd.read_excel(file, header=header, usecols=usecols)

    def json_load(self) -> dict:
        file = self.new_file()
        with open(file, 'r', encoding='utf-8') as f:
            return json.load(f)
