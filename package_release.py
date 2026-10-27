"""Package an explicit allowlist, excluding secrets and installed dependencies."""
import hashlib
import json
from pathlib import Path
from zipfile import ZipFile, ZIP_DEFLATED

ROOT = Path(__file__).resolve().parent
FILES = ['README.md', 'VERIFICATION.md', 'DEPLOYMENTS.json', 'pipeline_def.py', 'build_pipeline.py', 'create_entries.py', 'extra_entries.py', 'entries.json', 'pipeline.joblib', 'artifact-metadata.json', 'serve.py', 'modal_serve.py', 'requirements.txt', 'requirements-dev.txt', 'requirements-lock.txt', 'make_postman.py', 'verify_live.py', 'package_release.py', '.gitignore', 'frontend/package.json', 'frontend/package-lock.json', 'frontend/index.html', 'frontend/vercel.json', 'frontend/.env.example', 'frontend/playwright.config.js', 'tools/package.json', 'tools/package-lock.json']
DIRECTORIES = ['tests', 'corpus', 'frontend/src', 'frontend/tests', 'postman', 'evidence']

def main():
    paths = [ROOT / name for name in FILES + ['corpus_expansion.py', 'CORPUS_NOTES.md', 'extract_postman_responses.py', 'frontend/capture-report.mjs', 'DESIGN.md'] if (ROOT / name).is_file()]
    for name in DIRECTORIES:
        directory = ROOT / name
        if directory.exists():
            paths.extend(p for p in directory.rglob('*') if p.is_file() and '__pycache__' not in p.parts)
    paths = sorted(set(paths))
    target = ROOT / 'releases'
    target.mkdir(exist_ok=True)
    manifest = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
    with ZipFile(target / 'Error-Decoder.zip', 'w', ZIP_DEFLATED) as archive:
        for path in paths:
            archive.write(path, 'Error-Decoder/' + path.relative_to(ROOT).as_posix())
        archive.writestr('Error-Decoder/SHA256SUMS.json', json.dumps(manifest, indent=2))
    with ZipFile(target / 'Error-Decoder.zip') as archive:
        assert archive.testzip() is None
        assert not any('/node_modules/' in p or '/.venv/' in p or p.endswith('.env.local') for p in archive.namelist())
    print(f'Packaged and verified {len(paths)} files: {target / "Error-Decoder.zip"}')

if __name__ == '__main__':
    main()
