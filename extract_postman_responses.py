"""Extract readable responses from the unmodified official Postman CLI report."""
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent
report = json.loads((ROOT / 'evidence/postman-run.json').read_text(encoding='utf-8'))['run']
records = []
for execution in report['executions']:
    request = execution['requestExecuted']
    response = execution['response']
    url = request['url']
    raw = bytes(response['stream']['data']).decode('utf-8')
    records.append({'name': request['name'], 'method': request['method'], 'url': url['protocol'] + '://' + '.'.join(url['host']) + '/' + '/'.join(url['path']), 'request_body': request.get('body'), 'status': response['code'], 'response_time_ms': response['responseTime'], 'response': json.loads(raw), 'assertions': execution['tests']})
target = ROOT / 'evidence/postman-responses-readable.json'
target.write_text(json.dumps({'source': 'postman-run.json exported by official Postman CLI 1.56.3', 'summary': report['summary'], 'responses': records}, indent=2), encoding='utf-8')
assert len(records) == 10 and report['summary']['tests']['failed'] == 0
print(f'Extracted {len(records)} actual responses to {target}')
