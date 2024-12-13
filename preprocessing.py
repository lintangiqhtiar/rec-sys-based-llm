import pandas as pd

df = pd.read_csv('playstore_reviews.csv')
print(df.head(5))

print(df.info)