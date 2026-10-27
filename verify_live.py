"""Capture actual HTTP responses and verify exact frontend CORS configuration."""
import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
import httpx

parser = argparse.ArgumentParser()
parser.add_argument('--api', required=True)
parser.add_argument('--origin', required=True)
parser.add_argument('--output', default='evidence/live-http-responses.json')
args = parser.parse_args()
records = []
cases = [('GET', '/health', None, 200), ('GET', '/pipeline-info', None, 200), ('POST', '/search', {'text': "ModuleNotFoundError: No module named 'requests'", 'top_k': 3}, 200), ('POST', '/search', {'text': ' \n\t'}, 422), ('POST', '/search', {'text': 'zxqvblrp qqqzzzyyy'}, 200)]
with httpx.Client(base_url=args.api.rstrip('/'), timeout=120) as client:
    for method, path, body, expected in cases:
        response = client.request(method, path, json=body, headers={'Origin': args.origin})
        records.append({'method': method, 'url': str(response.url), 'request': body, 'status': response.status_code, 'response': response.json(), 'cors_origin': response.headers.get('access-control-allow-origin')})
        assert response.status_code == expected, records[-1]
        assert response.headers.get('access-control-allow-origin') == args.origin
    preflight = client.options('/search', headers={'Origin': args.origin, 'Access-Control-Request-Method': 'POST', 'Access-Control-Request-Headers': 'content-type'})
    assert preflight.status_code == 200 and preflight.headers['access-control-allow-origin'] == args.origin
target = Path(args.output)
target.parent.mkdir(exist_ok=True, parents=True)
target.write_text(json.dumps({'captured_at': datetime.now(timezone.utc).isoformat(), 'tool': 'httpx (separate from Postman evidence)', 'api': args.api, 'frontend_origin': args.origin, 'preflight_status': preflight.status_code, 'responses': records}, indent=2), encoding='utf-8')
print(f'Passed {len(cases)} live HTTP cases and CORS preflight; saved {target}')
