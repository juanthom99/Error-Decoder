"""Deploy with: modal deploy modal_serve.py (set CORS_ORIGINS first)."""
import json
import os
from pathlib import Path
import modal

ROOT = Path(__file__).resolve().parent
metadata = json.loads((ROOT / 'artifact-metadata.json').read_text(encoding='utf-8'))
requirements = (ROOT / 'requirements.txt').read_text(encoding='utf-8').splitlines()
if f"scikit-learn=={metadata['sklearn_version']}" not in requirements:
    raise RuntimeError('requirements.txt must pin the artifact scikit-learn version exactly')
origins = os.environ.get('CORS_ORIGINS', '')
if not origins or any(not o.strip().startswith('https://') for o in origins.split(',')):
    raise RuntimeError('Set CORS_ORIGINS to the exact HTTPS Vercel frontend origin(s) before deployment')
image = modal.Image.debian_slim(python_version='3.14').pip_install(*requirements).env({'CORS_ORIGINS': origins})
for filename in ('serve.py', 'pipeline_def.py', 'pipeline.joblib', 'artifact-metadata.json', 'requirements.txt'):
    image = image.add_local_file(ROOT / filename, f'/root/{filename}')
app = modal.App('error-decoder', image=image)


@app.function(timeout=120, scaledown_window=300, max_containers=2)
@modal.asgi_app()
def api():
    from serve import app as fastapi_app
    return fastapi_app
