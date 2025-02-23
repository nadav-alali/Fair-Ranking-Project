import os

import pandas as pd

from Datasets.Dataset import Dataset

def toy_oracle(order):
    count = {'blue': 0, 'orange': 0}
    for attr in order[-4:]:
        count[attr[2]] += 1
    return count['blue'] == count['orange']


class Toy(Dataset):
    def __init__(self, attribute1='x', attribute2='y'):
        df = self.__load_and_preprocess(attribute1, attribute2)
        super(Toy, self).__init__(df, attribute1, attribute2, ['color'])
        self.set_oracle(toy_oracle)

    def __len__(self):
        return len(self.attributes)

    def __load_and_preprocess(self, attribute1, attribute2):
        # load the dataset
        curr_path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(curr_path, "toy_data.csv")
        df = pd.read_csv(path)
        return df