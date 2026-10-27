"""Generate a Postman v2.1 collection with executable assertions."""
import json
import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def item(name, method, path, status, body=None, checks=()):
    request = {'method': method, 'header': [], 'url': '{{base_url}}' + path}
    if body is not None:
        request['header'] = [{'key': 'Content-Type', 'value': 'application/json'}]
        request['body'] = {'mode': 'raw', 'raw': json.dumps(body, indent=2), 'options': {'raw': {'language': 'json'}}}
    script = [f"pm.test('HTTP {status}', () => pm.response.to.have.status({status}));", "const data = pm.response.json();", *checks]
    return {'name': name, 'request': request, 'event': [{'listen': 'test', 'script': {'type': 'text/javascript', 'exec': script}}]}

def main():
    collection = {'info': {'name': 'Error Decoder — public API verification', 'description': 'Curated retrieval with a saved normalizer + TF-IDF pipeline. Set base_url to the deployed Modal HTTPS URL. No authentication is required by this API.', 'schema': 'https://schema.getpostman.com/json/collection/v2.1.0/collection.json'}, 'variable': [{'key': 'base_url', 'value': os.environ.get('API_BASE_URL', 'http://127.0.0.1:8000')}], 'item': [
        item('Health — ready', 'GET', '/health', 200, checks=["pm.test('Ready', () => pm.expect(data.status).to.eql('ready'));"]),
        item('Pipeline — fitted metadata', 'GET', '/pipeline-info', 200, checks=[
            "pm.test('1000-entry corpus', () => pm.expect(data.corpus_size).to.eql(1000));",
            "pm.test('Saved pipeline', () => { pm.expect(data.fitted).to.eql(true); pm.expect(data.serving_refits).to.eql(false); pm.expect(data.steps.map(s => s.class)).to.eql(['ErrorTextNormalizer', 'TfidfVectorizer']); });",
            "pm.test('Version and timestamp', () => { pm.expect(data.sklearn_version).to.eql('1.9.1'); pm.expect(Number.isNaN(Date.parse(data.build_timestamp))).to.eql(false); pm.expect(data.vocabulary_size).to.be.above(0); });"]),
        item('Valid search — module missing', 'POST', '/search', 200, {'text': "ModuleNotFoundError: No module named 'requests'", 'top_k': 3}, [
            "pm.test('Three results', () => pm.expect(data.results).to.have.lengthOf(3));",
            "pm.test('Relevant first match', () => pm.expect(data.results[0].title).to.eql('Missing installed module'));"] + search_checks()),
        item('Valid search — pandas', 'POST', '/search', 200, {'text': 'ValueError: The truth value of a Series is ambiguous'}, ["pm.test('Relevant pandas match', () => pm.expect(data.results[0].title).to.eql('Ambiguous Series truth'));"] + search_checks()),
        item('Unknown vocabulary — empty results', 'POST', '/search', 200, {'text': 'zxqvblrp qqqzzzyyy'}, ["pm.test('Clear no-match result', () => { pm.expect(data.results).to.eql([]); pm.expect(data.message).to.include('No matching vocabulary'); });"]),
        *[item(name, 'POST', '/search', 422, body, ["pm.test('Validation details', () => { pm.expect(data.detail).to.be.an('array').that.is.not.empty; data.detail.forEach(e => pm.expect(e).not.to.have.property('input')); });"]) for name, body in [
            ('Invalid — blank text', {'text': ' \n\t'}),
            ('Invalid — extra field', {'text': 'KeyError', 'unexpected': True}),
            ('Invalid — top_k outside range', {'text': 'KeyError', 'top_k': 6}),
            ('Invalid — noninteger top_k', {'text': 'KeyError', 'top_k': '3'}),
            ('Invalid — text too long', {'text': 'x' * 5001}),
        ]]]
    }
    target = ROOT / 'postman'
    target.mkdir(exist_ok=True)
    (target / 'Error-Decoder.postman_collection.json').write_text(json.dumps(collection, indent=2), encoding='utf-8')

def search_checks():
    return ["pm.test('Ranked similarity scores and entry content', () => { let previous = 1; data.results.forEach(r => { pm.expect(r.similarity).to.be.within(0, previous); previous = r.similarity; ['id', 'title', 'example_error', 'explanation', 'likely_cause', 'fix'].forEach(k => pm.expect(r[k]).to.be.a('string').that.is.not.empty); pm.expect(r.tags).to.be.an('array'); }); });"]

if __name__ == '__main__':
    main()
