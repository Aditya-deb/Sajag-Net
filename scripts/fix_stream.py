import pandas as pd
from sklearn.model_selection import train_test_split
import os

print("Rebuilding stream with source_index...")
df = pd.read_parquet(os.path.join("data", "processed", "cleaned_subset.parquet"))
df = df.reset_index(names=['source_index'])

X = df.drop(columns=["Label"])
y = df["Label"]
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

test_df = X_test.copy()
test_df["Label"] = y_test
sample_df = test_df.sample(n=1000, random_state=42)
sample_df.to_csv(os.path.join("data", "sample_stream.csv"), index=False)
print("Stream rebuilt successfully!")
