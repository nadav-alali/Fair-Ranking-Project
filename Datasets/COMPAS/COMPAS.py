import pandas as pd
from Datasets.Dataset import Dataset
from Oracle import Oracle
import os


class COMPAS(Dataset):
    dataset_file = 'compas-scores-two-years-violent.csv'
    scoring_attr = ['c_days_from_compas', 'juv_other_count', 'days_b_screening_arrest', 'start', 'end', 'age', 'priors_count']
    type_atts = ['sex', 'age_binary', 'age_bucketized', 'race']

    def __init__(self, attribute1='age', attribute2='juv_other_count', constraints=None, top_k_fraction=0.3):
        df = self.__load_and_preprocess(attribute1, attribute2)
        super(COMPAS, self).__init__(df, attribute1, attribute2, list(constraints.keys()))
        self.set_oracle(Oracle(constraints, top_k_fraction))

    def __len__(self):
        return len(self.attributes)

    def __load_and_preprocess(self, attribute1, attribute2):
        # load the dataset
        curr_path = os.path.dirname(os.path.realpath(__file__))
        path = os.path.join(curr_path, "compas-scores-two-years-violent.csv")
        df = pd.read_csv(path)

        attributes = [attribute1, attribute2]
        df = df.dropna(subset=attributes)

        # create a binary groups for 'age'
        df['age_binary'] = df['age'].apply(lambda x: '<36' if x < 35 else '>=36')
        df['age_bucketized'] = df['age'].apply(lambda x: '<30' if x < 30 else ('31-40' if 30 < x <= 40 else '>40'))

        df['age'] *= -1

        return df

