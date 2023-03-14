import pandas as pd

from aflight.client import predict

df = pd.read_csv("xtest.csv", index_col=0)
df = df.reset_index(drop=True)

output = predict(df)
print(output)
