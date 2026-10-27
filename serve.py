"""Stateless troubleshooting retrieval. Only load trusted, locally built artifacts."""
import os
import warnings
from pathlib import Path
import joblib
import numpy as np
import sklearn
from sklearn.exceptions import InconsistentVersionWarning
from sklearn.metrics.pairwise import cosine_similarity
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from pydantic import BaseModel, ConfigDict, Field, field_validator


def load_artifact(path):
    try:
        with warnings.catch_warnings():
            warnings.simplefilter('error', InconsistentVersionWarning)
            artifact = joblib.load(path)
        meta = artifact['metadata']
        if meta['sklearn_version'] != sklearn.__version__ or meta['schema_version'] != 1:
            raise ValueError('Incompatible artifact')
        pipeline, vectors, entries = artifact['pipeline'], artifact['document_vectors'], artifact['entries']
        probe = pipeline.transform(['KeyError'])
        if vectors.shape != (len(entries), probe.shape[1]) or not entries or not np.isfinite(vectors.data).all():
            raise ValueError('Invalid document vectors')
        if meta['corpus_size'] != len(entries):
            raise ValueError('Invalid corpus metadata')
        for entry in entries:
            for key in ('id', 'title', 'example_error', 'explanation', 'likely_cause', 'fix', 'tags'):
                if not entry[key]:
                    raise ValueError('Invalid entry')
        return artifact
    except Exception:
        return None


ARTIFACT = load_artifact(Path(os.getenv('PIPELINE_PATH', Path(__file__).with_name('pipeline.joblib'))))
app = FastAPI(title='Error Decoder', version='1.0.0')
app.add_middleware(CORSMiddleware, allow_origins=[v.strip().rstrip('/') for v in os.getenv('CORS_ORIGINS', 'http://localhost:5173,http://127.0.0.1:5173').split(',') if v.strip()], allow_methods=['GET', 'POST'], allow_headers=['Content-Type'])


class SearchRequest(BaseModel):
    model_config = ConfigDict(extra='forbid', strict=True)
    text: str = Field(min_length=1, max_length=5000)
    top_k: int = Field(default=3, ge=1, le=5)

    @field_validator('text')
    @classmethod
    def nonblank(cls, value):
        if not value.strip():
            raise ValueError('Text must contain a non-whitespace character')
        return value


@app.exception_handler(RequestValidationError)
async def validation_error(request, exc):
    # Do not echo potentially sensitive pasted errors in validation responses.
    return JSONResponse(status_code=422, content={'detail': [{'loc': list(e['loc']), 'msg': e['msg'], 'type': e['type']} for e in exc.errors()]})


def ready():
    if ARTIFACT is None:
        raise HTTPException(503, 'Search artifact unavailable. Build or restore a compatible pipeline.joblib and restart the service.')
    return ARTIFACT


@app.get('/', include_in_schema=False)
def homepage():
    return {
        'service': 'Error Decoder API',
        'hosting': 'Modal' if os.getenv('MODAL_TASK_ID') else 'Local',
        'status': 'ready' if ARTIFACT is not None else 'unavailable',
        'modal_app': 'error-decoder',
        'modal_deployment': 'https://modal.com/apps/juanthom99/main/deployed/error-decoder',
        'docs': '/docs',
        'health': '/health',
        'search': {'method': 'POST', 'path': '/search'},
        'frontend': 'https://error-decoder-orpin.vercel.app',
    }


@app.get('/health')
def health():
    ready()
    return {'status': 'ready'}


@app.get('/pipeline-info')
def pipeline_info():
    return {**ready()['metadata'], 'fitted': True, 'ranking': 'cosine similarity', 'serving_refits': False}


@app.post('/search')
def search(body: SearchRequest):
    artifact = ready()
    query = artifact['pipeline'].transform([body.text])
    if query.nnz == 0:
        return {'results': [], 'message': 'No matching vocabulary. Try the error name and its message in English.'}
    scores = cosine_similarity(query, artifact['document_vectors']).ravel()
    indices = np.argsort(-scores, kind='stable')[:body.top_k]
    results = [{**artifact['entries'][int(i)], 'similarity': float(np.clip(scores[i], 0, 1))} for i in indices if scores[i] > 0]
    return {'results': results, 'message': 'Matches ranked by text similarity, not confidence.' if results else 'No matching entries.'}
