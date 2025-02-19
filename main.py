import pandas as pd

df = pd.read_csv('Datasets/COMPAS/compas-scores-raw.csv').drop_duplicates(subset='Person_ID', keep='first')
print(df.head())