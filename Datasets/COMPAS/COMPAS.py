import pandas as pd
from Datasets.Dataset import Dataset
from Oracle import Oracle


class COMPAS(Dataset):
    def __init__(self, attribute1, attribute2):
        df = pd.read_csv('Datasets/COMPAS/compas-scores-raw.csv').drop_duplicates(subset='Person_ID', keep='first')
        df = df.sort_values(by=attribute1)
        super(COMPAS, self).__init__(df, attribute1, attribute2, 'Ethnic_Code_Text')
        self.set_oracle(Oracle('AfricanAmerican'))
