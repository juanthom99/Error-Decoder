"""Fit once offline; never called by the API."""
import json
import platform
from pathlib import Path
from datetime import datetime, timezone
import joblib
import sklearn
from sklearn.pipeline import Pipeline
from sklearn.feature_extraction.text import TfidfVectorizer
from pipeline_def import ErrorTextNormalizer

ROOT = Path(__file__).resolve().parent


def build(output=ROOT / 'pipeline.joblib'):
    entries = json.loads((ROOT / 'entries.json').read_text(encoding='utf-8'))
    assert len(entries) == 1000 and len({e['id'] for e in entries}) == 1000
    # Keep exact diagnostic terms prominent as the corpus grows; all ranking still
    # comes from the saved TF-IDF vectors and cosine similarity.
    documents = [' '.join([e['example_error']] * 10 + [e['title'], e['explanation'], e['likely_cause'], e['fix'], ' '.join(e['tags'])]) for e in entries]
    pipeline = Pipeline([('normalizer', ErrorTextNormalizer()), ('tfidf', TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True))])
    vectors = pipeline.fit_transform(documents)
    built_at = datetime.now(timezone.utc).isoformat()
    metadata = {'schema_version': 1, 'steps': [{'name': name, 'class': type(step).__name__} for name, step in pipeline.steps], 'built_at': built_at, 'build_timestamp': built_at, 'sklearn_version': sklearn.__version__, 'python_version': platform.python_version(), 'corpus_size': len(entries), 'vocabulary_size': len(pipeline.named_steps['tfidf'].vocabulary_)}
    artifact = {'pipeline': pipeline, 'document_vectors': vectors, 'entries': entries, 'metadata': metadata}
    joblib.dump(artifact, output)
    (ROOT / 'artifact-metadata.json').write_text(json.dumps(metadata, indent=2), encoding='utf-8')
    print(json.dumps(metadata, indent=2))
    return artifact


if __name__ == '__main__':
    build()
