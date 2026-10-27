# Screenshot guide

All images are in `screenshots/`. The public app is https://error-decoder-orpin.vercel.app and its API is https://juanthom99--error-decoder-api.modal.run. Browser screenshots capture webpage content; the browser address bar is not part of a Playwright page screenshot. URLs and capture provenance are recorded in `screenshot-provenance.json`.

## Screenshot index

| File | What it proves |
| --- | --- |
| app-initial-desktop.png | Deployed app, large input, examples, ready status |
| glass-dropdown-desktop.png | Open glass Matches dropdown |
| glass-dropdown-mobile.png | Mobile dropdown layout |
| app-search-desktop.png | Actual live search, explanations, causes, fixes, similarity scores |
| app-results-desktop.png | Live results and expanded fitted pipeline metadata |
| app-results-mobile.png | Responsive mobile layout with results and pipeline details |
| expanded-corpus-phone-mobile.png | New corpus match and 1,000-entry pipeline metadata at phone width |
| app-no-match-desktop.png | Unknown vocabulary produces a clear empty state |
| app-validation-desktop.png | Blank input validation |
| app-simulated-503-desktop.png | Unavailable-state handling using an intentionally simulated 503 |
| postman-01-summary.png | Official Postman run: 25 passing assertions |
| postman-02-all-requests.png | Ten public requests and their actual HTTP statuses |
| postman-03-health-200.png | Actual readiness response and assertions |
| postman-04-pipeline-200.png | Actual fitted metadata response and assertions |
| postman-05-valid-search-200.png | Actual valid request, matching entries, and assertions |
| postman-06-invalid-search-422.png | Actual invalid request, validation response, and assertions |
| deployment-api-documentation.png | Public Modal API documentation and all three endpoints |

The remaining `*-mobile.png` files provide mobile evidence for the initial, validation, no-match, and simulated-unavailable states.

Postman screenshots show the **actual HTML run report exported by the official Postman CLI**, not the desktop Postman application. Raw complete responses are preserved in `postman-run.json`, `postman-run.html`, and `postman-responses-readable.json`. The response viewer may scroll long responses; consult the JSON for every returned entry.

Deployment evidence is the app captured from its public Vercel production URL, live Modal documentation, and real requests to the public API. No authenticated deployment-dashboard screenshot is claimed.
