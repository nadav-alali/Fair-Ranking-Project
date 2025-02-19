from Datasets.Dataset import Dataset
import pandas as pd


class COMPAS(Dataset):
    def __init__(self, attribute1, attribute2):
        path = 'Datasets/COMPAS/compas-scores-raw.csv'
        super(COMPAS, self).__init__(path, attribute1, attribute2)


