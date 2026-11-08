import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.tree import DecisionTreeClassifier
from lightgbm import LGBMClassifier

LABEL = "Label"

df = pd.read_parquet("data/processed/cleaned_subset.parquet")
df.columns = df.columns.str.strip().str.replace(" ", "_")

print(df[LABEL].value_counts(), "\n")
print(f"exact duplicate rows: {df.duplicated().sum()} ({df.duplicated().mean():.1%})")

X, y = df.drop(columns=[LABEL]), df[LABEL]
X_tr, X_te, y_tr, y_te = train_test_split(
    X, y, test_size=0.2, stratify=y, random_state=42)

h_tr = set(pd.util.hash_pandas_object(X_tr, index=False))
h_te = pd.util.hash_pandas_object(X_te, index=False)
print(f"test rows identical to a train row: {h_te.isin(h_tr).mean():.1%}")

port_cols = [c for c in X.columns if "port" in c.lower()]
print("port-like columns:", port_cols)

def run(name, model, cols):
    model.fit(X_tr[cols], y_tr)
    pred = model.predict(X_te[cols])
    print(f"\n=== {name} ===")
    print(classification_report(y_te, pred, digits=4))
    print(confusion_matrix(y_te, pred, labels=model.classes_))
    print("class order:", list(model.classes_))

all_cols = list(X.columns)
no_port = [c for c in all_cols if c not in port_cols]
run("Decision Tree baseline", DecisionTreeClassifier(max_depth=8, random_state=42), all_cols)
run("LightGBM (all features)", LGBMClassifier(n_estimators=100, verbose=-1), all_cols)
run("LightGBM (no port columns)", LGBMClassifier(n_estimators=100, verbose=-1), no_port)
