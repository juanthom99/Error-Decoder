import importlib
import json
from pathlib import Path
from collections import Counter
import joblib
import numpy as np
import pytest
from fastapi.testclient import TestClient
from sklearn.base import clone
import serve
from pipeline_def import ErrorTextNormalizer

ROOT = Path(__file__).resolve().parents[1]
client = TestClient(serve.app)


def test_corpus_and_roundtrip(tmp_path):
    artifact = serve.ARTIFACT
    assert artifact is not None
    entries = artifact['entries']
    assert len(entries) == 1000
    assert Counter(e['tags'][0] for e in entries) == {'python': 350, 'pandas': 250, 'pip': 175, 'fastapi': 225}
    assert len({e['example_error'] for e in entries}) == 1000
    assert len({e['title'] for e in entries}) == 1000
    queries = [e['example_error'] for e in entries]
    before = artifact['pipeline'].transform(queries)
    path = tmp_path / 'roundtrip.joblib'
    joblib.dump(artifact, path)
    restored = joblib.load(path)
    assert (before != restored['pipeline'].transform(queries)).nnz == 0
    assert (artifact['document_vectors'] != restored['document_vectors']).nnz == 0


def test_normalizer_clone_and_traceback():
    normalizer = clone(ErrorTextNormalizer())
    assert normalizer.fit(['a']) is normalizer
    a = '  File "C:\\work\\one.py", line 22, in first\nKeyError: USER 0xABC123'
    b = 'File "/tmp/two.py", line 99, in second\nKeyError: USER 0x123456'
    assert normalizer.transform([a]) == normalizer.transform([b])
    assert 'keyerror' in normalizer.transform([a])[0]
    assert ErrorTextNormalizer(lowercase=False).transform([' KeyError  X ']) == ['KeyError X']


def test_health_and_info():
    assert client.get('/health').json() == {'status': 'ready'}
    info = client.get('/pipeline-info').json()
    assert info['corpus_size'] == 1000 and info['fitted'] is True
    assert info['serving_refits'] is False
    assert info['sklearn_version'] == serve.sklearn.__version__
    assert info['built_at'] == info['build_timestamp']
    from datetime import datetime
    assert datetime.fromisoformat(info['built_at']).tzinfo is not None


@pytest.mark.parametrize('body', [
    {}, {'text': ''}, {'text': ' \n\t'}, {'text': 'x' * 5001},
    {'text': 5}, {'text': None}, {'text': 'error', 'extra': True},
    *[{'text': 'error', 'top_k': v} for v in [0, 6, -1, 2.5, '3', True, None]],
])
def test_invalid_requests(body):
    response = client.post('/search', json=body)
    assert response.status_code == 422
    assert all('input' not in detail for detail in response.json()['detail'])


@pytest.mark.parametrize('text', ['x', 'x' * 5000])
def test_valid_text_bounds(text):
    assert client.post('/search', json={'text': text}).status_code == 200


@pytest.mark.parametrize('k', [1, 3, 5])
def test_top_k(k):
    response = client.post('/search', json={'text': 'ValueError', 'top_k': k})
    assert response.status_code == 200
    results = response.json()['results']
    assert len(results) == k
    scores = [r['similarity'] for r in results]
    assert scores == sorted(scores, reverse=True)
    assert all(0 < score <= 1 for score in scores)


def test_default_top_k_and_unknown():
    assert len(client.post('/search', json={'text': 'ValueError'}).json()['results']) == 3
    data = client.post('/search', json={'text': 'zxqvblrp qqqzzzyyy'}).json()
    assert data['results'] == [] and 'No matching vocabulary' in data['message']


@pytest.mark.parametrize('query,title', [
    ("ModuleNotFoundError: No module named 'httpx'", 'Missing installed module'),
    ('pandas Series if condition truth value ambiguous', 'Ambiguous Series truth'),
    ('pip dependency resolver ResolutionImpossible conflicting dependencies', 'Dependency resolution conflict'),
    ('ResponseValidationError response field required FastAPI', 'Response model mismatch'),
    ("TypeError: 'NoneType' object is not subscriptable", 'None used as a subscript'),
    ("AttributeError: 'NoneType' object has no attribute 'group'", 'No regex match'),
    ("ValueError: cannot reindex on an axis with duplicate labels", 'Duplicate labels prevent reindexing'),
    ('pip wheel not supported on this platform', 'Wheel platform incompatible'),
    ('422 Unprocessable Entity loc query q Field required', 'Missing query parameter'),
    ('422 Unprocessable Entity loc body name Field required', 'Missing request body field'),
    ('Decimal plus float unsupported operand types', 'Decimal mixed with float'),
    ('json dumps recursive container Circular reference detected', 'JSON circular reference'),
    ('slice step cannot be zero in items slicing', 'Zero slice step'),
    ('bytes fromhex non-hexadecimal number invalid input', 'Malformed hexadecimal input'),
    ('pandas read csv postal identifiers lose leading zeroes', 'CSV leading zeros disappear'),
    ('pandas groupby first combines nonmissing fields from different source rows', 'Groupby first combines values from different rows'),
    ('pandas dt seconds duration loses whole days', 'Timedelta seconds component mistaken for total'),
    ('pandas iterrows changing row does not update original dataframe', 'Modifying iterrows row has no effect'),
    ('pip install --dry-run says installed but cannot import package', 'Pip dry run does not install anything'),
    ('pip only binary source-only distribution has no wheel', 'Only binary excludes source-only package'),
    ('pip build fails rustc compiler too old minimum rust version', 'Rust minimum version not satisfied'),
    ('pip Docker builder installed dependencies missing final image stage', 'Docker dependencies installed in discarded stage'),
    ('FastAPI huge integer identifier loses precision in JavaScript browser', 'Response integer outside JavaScript safe range'),
    ('FastAPI Depends get_db called parentheses generator instead of callable', 'Depends function called during declaration'),
    ('FastAPI async time.sleep blocks concurrent requests', 'Blocking sleep freezes concurrent requests'),
    ('FastAPI Vite frontend still calls old API after environment URL changed', 'Frontend build uses stale API base URL'),
])
def test_relevant_ranking(query, title):
    results = client.post('/search', json={'text': query}).json()['results']
    assert results[0]['title'] == title, [r['title'] for r in results]


def test_every_example_ranks_own_entry_first():
    failures = []
    for entry in serve.ARTIFACT['entries']:
        result = client.post('/search', json={'text': entry['example_error'], 'top_k': 1}).json()['results'][0]
        if result['id'] != entry['id']:
            failures.append((entry['id'], entry['title'], result['title']))
    assert not failures, failures


def test_serving_never_refits(monkeypatch):
    pipeline = serve.ARTIFACT['pipeline']
    vocabulary = dict(pipeline.named_steps['tfidf'].vocabulary_)
    idf = pipeline.named_steps['tfidf'].idf_.copy()
    def forbidden(*args, **kwargs):
        raise AssertionError('Serving refitted the model')
    for obj in (pipeline, *pipeline.named_steps.values()):
        monkeypatch.setattr(obj, 'fit', forbidden)
        monkeypatch.setattr(obj, 'fit_transform', forbidden)
    assert client.post('/search', json={'text': 'KeyError username'}).status_code == 200
    assert pipeline.named_steps['tfidf'].vocabulary_ == vocabulary
    np.testing.assert_array_equal(pipeline.named_steps['tfidf'].idf_, idf)


@pytest.mark.parametrize('kind', ['missing', 'corrupt', 'version', 'shape', 'schema'])
def test_unavailable_artifacts_at_import(kind, tmp_path, monkeypatch):
    path = tmp_path / 'bad.joblib'
    if kind == 'corrupt':
        path.write_bytes(b'not a joblib artifact')
    elif kind != 'missing':
        artifact = joblib.load(ROOT / 'pipeline.joblib')
        if kind == 'version': artifact['metadata']['sklearn_version'] = '0.0.0'
        if kind == 'shape': artifact['document_vectors'] = artifact['document_vectors'][:1]
        if kind == 'schema': artifact['metadata']['schema_version'] = -1
        joblib.dump(artifact, path)
    monkeypatch.setenv('PIPELINE_PATH', str(path))
    try:
        importlib.reload(serve)
        broken = TestClient(serve.app)
        assert broken.get('/health').status_code == 503
        assert broken.get('/pipeline-info').status_code == 503
        assert broken.post('/search', json={'text': 'KeyError'}).status_code == 503
        assert broken.post('/search', json={'text': ''}).status_code == 422
    finally:
        monkeypatch.delenv('PIPELINE_PATH')
        importlib.reload(serve)


def test_loads_once(monkeypatch):
    def forbidden(*args, **kwargs): raise AssertionError('Reloaded artifact per request')
    monkeypatch.setattr(joblib, 'load', forbidden)
    assert TestClient(serve.app).post('/search', json={'text': 'KeyError'}).status_code == 200


def test_cors():
    response = client.options('/search', headers={'Origin': 'http://localhost:5173', 'Access-Control-Request-Method': 'POST', 'Access-Control-Request-Headers': 'content-type'})
    assert response.status_code == 200
    assert response.headers['access-control-allow-origin'] == 'http://localhost:5173'
    denied = client.options('/search', headers={'Origin': 'https://untrusted.example', 'Access-Control-Request-Method': 'POST'})
    assert 'access-control-allow-origin' not in denied.headers
