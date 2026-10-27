# Verification records

## Completed

- 1,000 original entries: Python 350, pandas 250, pip 175, FastAPI 225. Explicit editable corpus sources and editorial notes are included.
- Saved fitted normalizer → TF-IDF pipeline, document vectors, entries, and metadata.
- Exact scikit-learn 1.9.1 pin; saved artifact has 32,092 learned features.
- FastAPI readiness, pipeline information, and search endpoints.
- Strict validation, no-vocabulary response, artifact failure handling, no serving refit, and no application-level query storage.
- React frontend with examples, results, similarity labels, loading/validation/unavailable/no-match states, and expandable pipeline information.
- 58 backend tests passing; all 1,000 example errors retrieve their own entry first, and all 26 rephrased ranking regression queries pass.
- Modal API deployed: https://juanthom99--error-decoder-api.modal.run
- Vercel production frontend deployed: https://error-decoder-orpin.vercel.app
- Vercel production VITE_API_BASE_URL points directly to Modal; Modal CORS allows the exact production frontend origin.
- Five live HTTP checks plus CORS preflight passed.
- Official Postman CLI executed 10 public API requests; all 25 assertions passed.
- Actual valid (200), invalid (422), health, metadata, and no-match Postman responses saved as JSON and HTML.

## Browser verification

- All 12 Playwright browser tests passed against the glass-design production frontend: live search and pipeline details, blank validation and unknown vocabulary, simulated service unavailability, keyboard-operated match selection, layout bounds, and reduced motion, on desktop and mobile.
- Expanded-corpus results and pipeline details fit tested widths of 320, 375, 390, and 768 pixels. These are browser viewport/device-emulation checks, not a claim of testing on physical phones.
- The dark glass redesign follows the supplied UI mockup handoff while preserving real API search and fitted pipeline metadata.
- Successful browser searches went directly to the public Modal API; response URL and HTTP 200 were asserted.
- All 23 screenshots were refreshed after the 1,000-entry deployment. They include desktop/mobile app states, the original official Postman report and expanded responses, and public API documentation. See evidence/SCREENSHOT_GUIDE.md.
- The 503 screenshots deliberately simulate a failed API response; they do not claim the deployed API was unavailable during final verification.

## Evidence scope

The official Postman CLI ran the collection locally against the public API and saved the response evidence. These records do not claim a Postman cloud workspace upload.
