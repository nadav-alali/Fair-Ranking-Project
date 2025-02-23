from copy import deepcopy
from random import sample

import pandas as pd


class Dataset:
    def __init__(self, df, attribute1, attribute2, constraints_types):
        self.dataset = df
        self.attributes = self.dataset[[attribute1, attribute2] + constraints_types].values.tolist()
        self.oracle = None
        self.portion = self.dataset.shape[0]

    def __len__(self):
        return self.dataset.size

    def set_portion(self, portion):
        self.portion = portion

    def get_attributes(self) -> list:
        return sample(self.attributes, self.portion)

    def set_oracle(self, oracle):
        self.oracle = oracle

    def get_oracle(self):
        return self.oracle


