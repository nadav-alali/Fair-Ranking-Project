import pandas as pd


class Dataset:
    def __init__(self, path, attribute1, attribute2):
        self.dataset = pd.read_csv(path)
        self.attributes = self.dataset[[attribute1, attribute2]].values.tolist()
        self.oracle = None

    def get_attributes(self) -> list:
        return self.attributes

    def set_oracle(self, oracle):
        self.oracle = oracle

    def get_oracle(self):
        return self.oracle
