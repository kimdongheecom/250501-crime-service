from app.domain.model.matzip_schema import MatZipdata
import pandas as pd

class MatZipService:
    dataschema = MatZipdata()

    def new_model(self, fname) -> object:
        this = self.dataschema
        this.context = 'C:\\Users\\bitcamp\\Documents\\kpmg-250424\\kpmg2501\\V2\\ai-server\\matzip-service\\app\\domain\\stored_data\\'
        this.fname = fname
        return pd.read_csv(this.context + this.fname)
    

