import pandas as pd
import joblib
from sklearn.model_selection import train_test_split
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import accuracy_score, classification_report

class PhishingModel:
    def __init__(self, dosya_yolu):
        self.dosya_yolu = dosya_yolu
        self.veri = None
        self.vectorizer = TfidfVectorizer(analyzer='char', ngram_range=(3, 5), max_features=10000)
        self.model = LogisticRegression(max_iter=1000, random_state=42)
        
    def veri_yukle(self):
        self.veri = pd.read_csv(self.dosya_yolu)
        if 'URL' not in self.veri.columns or 'Label' not in self.veri.columns:
            raise ValueError("Veri setinde 'URL' veya 'Label' sütunu bulunamadı!")
            
    def modeli_egit_ve_kaydet(self):
        X = self.vectorizer.fit_transform(self.veri['URL'].astype(str))
        y = self.veri['Label'].map({'bad': 1, 'good': 0})
        
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        self.model.fit(X_train, y_train)
        
        y_pred = self.model.predict(X_test)
        acc = accuracy_score(y_test, y_pred)
        
        print(f"[RESULT] Accuracy: %{acc * 100:.2f}")
        print("[RESULT] Classification Report:\n", classification_report(y_test, y_pred))
        
        joblib.dump(self.model, 'phishing_model_nlp.pkl')
        joblib.dump(self.vectorizer, 'tfidf_vectorizer.pkl')

if __name__ == "__main__":
    sistem = PhishingModel("phishing_site_urls.csv")
    sistem.veri_yukle()
    sistem.modeli_egit_ve_kaydet()