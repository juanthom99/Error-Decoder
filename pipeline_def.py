"""Importable, pickle-safe text preprocessing shared by build and serving."""
import re
from sklearn.base import BaseEstimator, TransformerMixin


class ErrorTextNormalizer(BaseEstimator, TransformerMixin):
    def __init__(self, lowercase=True):
        self.lowercase = lowercase

    def fit(self, X, y=None):
        return self

    def transform(self, X):
        result = []
        for text in X:
            text = re.sub(r'File "[^"]+", line \d+(?:, in [^\n]+)?', ' traceback_frame ', text)
            text = re.sub(r'0x[0-9a-fA-F]+', ' memory_address ', text)
            text = re.sub(r'(?i)\bline \d+\b', 'line number', text)
            text = re.sub(r'(?i)https?://\S+', ' url ', text)
            if self.lowercase:
                text = text.lower()
            result.append(' '.join(text.split()))
        return result
