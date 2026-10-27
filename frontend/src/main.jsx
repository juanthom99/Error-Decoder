import React, {useEffect, useRef, useState} from 'react';
import {createRoot} from 'react-dom/client';
import './style.css';

const API = (import.meta.env.VITE_API_BASE_URL || (import.meta.env.DEV ? 'http://127.0.0.1:8000' : '')).replace(/\/$/, '');
const EXAMPLES = [
  ['Python', "ModuleNotFoundError: No module named 'requests'"],
  ['pandas', 'ValueError: The truth value of a Series is ambiguous'],
  ['pip', 'ERROR: ResolutionImpossible: conflicting dependencies'],
  ['FastAPI', 'fastapi.exceptions.ResponseValidationError: response field required'],
];

async function call(path, options = {}) {
  if (!API) throw new Error('The API URL is not configured. Set VITE_API_BASE_URL and rebuild the frontend.');
  let response;
  try { response = await fetch(`${API}${path}`, {...options, signal: AbortSignal.timeout(60000)}); }
  catch { throw new Error('The API could not be reached. It may be starting up or unavailable. Try again shortly.'); }
  if (response.status === 503) throw new Error('The search model is unavailable. Please try again after the service is restored.');
  if (response.status === 422) {
    const data = await response.json();
    throw new Error(data.detail?.map(e => e.msg).join(' · ') || 'Check your error text and number of matches.');
  }
  if (!response.ok) throw new Error(`The API returned an error (${response.status}). Please try again.`);
  return response.json();
}

function MatchesSelect({value, onChange, disabled}) {
  const [open, setOpen] = useState(false);
  const root = useRef(null);
  const trigger = useRef(null);
  useEffect(() => {
    function outside(event) { if (!root.current?.contains(event.target)) setOpen(false); }
    document.addEventListener('pointerdown', outside);
    return () => document.removeEventListener('pointerdown', outside);
  }, []);
  useEffect(() => {
    if (open) root.current.querySelector('[aria-selected="true"]')?.focus();
  }, [open]);
  useEffect(() => { if (disabled) setOpen(false); }, [disabled]);
  function keydown(event) {
    if (event.key === 'Escape') { event.preventDefault(); setOpen(false); trigger.current.focus(); }
    if (['ArrowDown', 'ArrowUp', 'Home', 'End'].includes(event.key)) {
      event.preventDefault();
      if (!open) { setOpen(true); return; }
      const options = [...root.current.querySelectorAll('[role="option"]')];
      const current = options.indexOf(document.activeElement);
      const next = event.key === 'Home' ? 0 : event.key === 'End' ? 4 : (current + (event.key === 'ArrowDown' ? 1 : -1) + 5) % 5;
      options[next].focus();
    }
  }
  return <div className="matches" ref={root} onKeyDown={keydown} onBlur={event => { if (!event.currentTarget.contains(event.relatedTarget)) setOpen(false); }}>
    <span id="matches-label">Matches</span>
    <button ref={trigger} type="button" className="matches-trigger" role="combobox" aria-labelledby="matches-label" aria-expanded={open} aria-controls="matches-options" aria-haspopup="listbox" disabled={disabled} onClick={() => setOpen(!open)}>{value}<span className={open ? 'chevron open' : 'chevron'} aria-hidden="true">⌄</span></button>
    {open && <div id="matches-options" role="listbox" aria-labelledby="matches-label" className="matches-menu">{[1,2,3,4,5].map(n => <button key={n} type="button" role="option" aria-selected={n === value} onClick={() => {onChange(n); setOpen(false); trigger.current.focus();}}>{n}<span aria-hidden="true">{n === value ? '✓' : ''}</span></button>)}</div>}
  </div>;
}

function App() {
  const [text, setText] = useState('');
  const [topK, setTopK] = useState(3);
  const [results, setResults] = useState(null);
  const [message, setMessage] = useState('');
  const [error, setError] = useState('');
  const [busy, setBusy] = useState(false);
  const [info, setInfo] = useState(null);
  const [infoError, setInfoError] = useState('');
  const [infoBusy, setInfoBusy] = useState(false);
  const [status, setStatus] = useState('Checking API');
  const input = useRef(null);
  async function loadInfo() {
    setInfoBusy(true); setInfoError('');
    try { const data = await call('/pipeline-info'); setInfo(data); setStatus('API ready'); }
    catch (e) { setInfoError(e.message); setStatus('API unavailable'); }
    finally { setInfoBusy(false); }
  }
  useEffect(() => { loadInfo(); }, []);
  function updateText(value) { setText(value); setResults(null); setError(''); setMessage(''); }
  async function search(event) {
    event.preventDefault();
    if (!text.trim() || [...text].length > 5000) { setError('Enter 1–5,000 characters, including at least one non-whitespace character.'); input.current.focus(); return; }
    setBusy(true); setError(''); setResults(null);
    try {
      const data = await call('/search', {method: 'POST', headers: {'Content-Type': 'application/json'}, body: JSON.stringify({text, top_k: topK})});
      setResults(data.results); setMessage(data.message); setStatus('API ready');
    } catch (e) { setError(e.message); }
    finally { setBusy(false); }
  }
  return <div className="app">
    <div className="ambient" aria-hidden="true"><div className="orb orb-blue"/><div className="orb orb-lime"/><div className="orb orb-violet"/></div>
    <header><a className="brand" href="/" aria-label="Error Decoder home"><span className="mark">&gt;_</span>error<span className="brand-light">decoder</span></a><div className="status"><i className={status === 'API ready' ? 'online' : ''}/>{status}</div></header>
    <main>
      <div className="intro"><div className="eyebrow">A LITTLE LESS TRACEBACK. A LITTLE MORE CLARITY.</div><h1>Make sense of<br/><span>what went wrong.</span></h1><p>Paste an error. Find matching explanations, likely causes, and practical fixes from {info ? info.corpus_size.toLocaleString('en-US') : '1,000'} curated entries.</p></div>
      <div className="workspace">
        <section className="input-panel" aria-labelledby="input-title"><div className="section-heading"><span className="step">01</span><h2 id="input-title">The error</h2><span className="small-label">INPUT</span></div>
          <form onSubmit={search} noValidate>
            <label htmlFor="error-text">Error message or traceback</label>
            <div className={'editor ' + (error ? 'has-error' : '')}><div className="editor-bar"><span><i/><i/><i/></span><span>traceback.txt</span><span>TEXT</span></div><textarea id="error-text" ref={input} value={text} disabled={busy} onChange={e => updateText(e.target.value)} placeholder={'Paste your error here…\n\nTraceback (most recent call last):\n  File "app.py", line 12, in <module>\nModuleNotFoundError: No module named \'requests\''} spellCheck="false" aria-describedby="input-help char-count" aria-invalid={Boolean(error)}/><div className="editor-footer"><span>Python · pandas · pip · FastAPI</span><span id="char-count" className={[...text].length > 5000 ? 'over-limit' : ''}>{[...text].length.toLocaleString()} / 5,000</span></div></div>
            <p id="input-help" className="privacy">Pasted errors are processed without application-level storage.</p>
            <div className="controls"><MatchesSelect value={topK} onChange={setTopK} disabled={busy}/><button className="primary" disabled={busy} type="submit">{busy ? <><span className="spinner"/>Finding matches…</> : <>Decode error <span aria-hidden="true">↗</span></>}</button></div>
            {error && <div className="notice error" role="alert">{error}</div>}
          </form>
          <div className="examples"><h3>Try an example</h3><div>{EXAMPLES.map(([tag, value]) => <button disabled={busy} key={tag} onClick={() => {updateText(value); input.current.focus();}}><span>{tag}</span><span aria-hidden="true">↗</span></button>)}</div></div>
        </section>
        <section className="results-panel" aria-labelledby="results-title" aria-busy={busy}><div className="section-heading"><span className="step">02</span><h2 id="results-title">Possible explanations</h2>{results?.length > 0 && <span className="count">{results.length}</span>}</div>
          <div aria-live="polite">
            {busy ? <div className="empty"><span className="large-symbol pulse">⌕</span><h3>Searching the knowledge base</h3><p>Comparing your error with the saved vocabulary.<br/>The API may take a moment to start.</p></div> : results === null ? <div className="empty"><div className="terminal-illustration"><span>&gt; error</span><div/><div/><b>?</b></div><h3>Start with the message.</h3><p>Your closest matches will appear here.<br/>Include the error name for a more useful match.</p><span className="empty-note">CURATED EXPLANATIONS · NO GENERATED ANSWERS</span></div> : results.length === 0 ? <div className="empty"><span className="large-symbol">∅</span><h3>No matching vocabulary</h3><p>{message}</p></div> : <><p className="result-caption">Ranked by text similarity. Scores are not confidence or a diagnosis.</p>{results.map((result, i) => <article className="result" key={result.id}><div className="result-top"><span className="tag">{result.tags.join(' / ')}</span><span className="score">{(result.similarity * 100).toFixed(1)}% <span>similarity</span></span></div><h3><span className="rank">{String(i+1).padStart(2,'0')}</span>{result.title}</h3><code>{result.example_error}</code><p>{result.explanation}</p><div className="cause"><strong>Likely cause</strong><p>{result.likely_cause}</p></div><div className="fix"><strong><span aria-hidden="true">↳ </span>Suggested fix</strong><p>{result.fix}</p></div></article>)}</>}
          </div>
        </section>
      </div>
      <details className="pipeline"><summary><span><span aria-hidden="true">⛭</span> Inside the fitted pipeline</span><span className="summary-hint">How matching works <span aria-hidden="true">＋</span></span></summary><div className="pipeline-body"><p>Your text is normalized, transformed with the saved TF-IDF vocabulary and IDF weights, then compared with the saved document vectors using cosine similarity. Serving never refits the model.</p>{infoBusy ? <p role="status">Loading pipeline information…</p> : infoError ? <div role="alert"><p>{infoError}</p><button onClick={loadInfo}>Retry pipeline information</button></div> : info && <><div className="pipeline-steps">{info.steps.map((step, i) => <React.Fragment key={step.name}>{i > 0 && <span aria-hidden="true">→</span>}<code>{step.class}</code></React.Fragment>)}<span aria-hidden="true">→</span><code>Cosine similarity</code></div><dl><div><dt>Corpus</dt><dd>{info.corpus_size} entries</dd></div><div><dt>Learned vocabulary</dt><dd>{info.vocabulary_size.toLocaleString()} features</dd></div><div><dt>scikit-learn</dt><dd>{info.sklearn_version}</dd></div><div><dt>Built (UTC)</dt><dd>{new Date(info.build_timestamp).toISOString().replace('T', ' ').slice(0,19)}</dd></div></dl></>}</div></details>
    </main><footer><span>error decoder <span className="footer-slash">/</span> English troubleshooting search</span><span>{info ? info.corpus_size.toLocaleString('en-US') : '1,000'} entries. One less mystery.</span></footer>
  </div>;
}
createRoot(document.getElementById('root')).render(<App/>);
