from copy import deepcopy


class Dataset:
    def __init__(self, df, attribute1, attribute2, protected_attr):
        self.dataset = df
        self.attributes = self.dataset[[attribute1, attribute2, protected_attr]].values.tolist()
        self.oracle = None

    def get_attributes(self) -> list:
        return deepcopy(self.attributes)

    def set_oracle(self, oracle):
        self.oracle = oracle

    def get_oracle(self):
        return self.oracle
