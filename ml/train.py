from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import classification_report
import joblib

from data_utils import gerar_dataset

df, X, y = gerar_dataset(n_samples=2000, seed=42)

X_train, X_test, y_train, y_test = train_test_split(
    X, y, test_size=0.2, random_state=42, stratify=y
)

model = RandomForestClassifier(n_estimators=100, random_state=42)
model.fit(X_train, y_train)

y_pred = model.predict(X_test)
print(classification_report(y_test, y_pred, target_names=["legítimo", "fraude"]))

joblib.dump(model, "model_fraude.pkl")
print("✅ Modelo guardado como 'model_fraude.pkl'")
