import {chromium} from '@playwright/test';
import {mkdir, writeFile} from 'node:fs/promises';
import {resolve} from 'node:path';
import {pathToFileURL} from 'node:url';

const out = resolve('../evidence/screenshots');
await mkdir(out, {recursive:true});
const browser = await chromium.launch();
const page = await browser.newPage({viewport:{width:1440,height:1100},deviceScaleFactor:1});
await page.goto(pathToFileURL(resolve('../evidence/postman-run.html')).href);
await page.getByRole('button',{name:'Summary',exact:true}).waitFor();
await page.screenshot({path:resolve(out,'postman-01-summary.png'),fullPage:true});
await page.getByRole('button',{name:'All Requests',exact:true}).click();
await page.screenshot({path:resolve(out,'postman-02-all-requests.png'),fullPage:true});
await page.setViewportSize({width:1440,height:2400});
for (const [name,file] of [
  ['Health — ready','postman-03-health-200.png'],
  ['Pipeline — fitted metadata','postman-04-pipeline-200.png'],
  ['Valid search — module missing','postman-05-valid-search-200.png'],
  ['Invalid — blank text','postman-06-invalid-search-422.png'],
]) {
  await page.getByText('Collapse All',{exact:true}).click();
  const label=page.locator('.execution-name').filter({hasText:name});
  await label.click();
  const card=label.locator('xpath=ancestor::div[contains(concat(" ",normalize-space(@class)," ")," dynamic-accordion ")][1]');
  for (const title of ['Request body','Response body']) {
    const section=card.getByText(title,{exact:true});
    if(await section.count()) await section.click();
  }
  const tests=card.getByText(/^Tests \(/);
  if(await tests.count()) await tests.click();
  await card.evaluate(element=>element.scrollIntoView({block:'center'}));
  await card.screenshot({path:resolve(out,file)});
}
await page.setViewportSize({width:1440,height:1100});
await page.goto('https://juanthom99--error-decoder-api.modal.run/docs');
await page.getByRole('heading',{name:'Error Decoder',exact:false}).waitFor();
await page.screenshot({path:resolve(out,'deployment-api-documentation.png'),fullPage:true});
await writeFile(resolve('../evidence/screenshot-provenance.json'),JSON.stringify({captured_at:new Date().toISOString(),frontend:'https://error-decoder-orpin.vercel.app',api:'https://juanthom99--error-decoder-api.modal.run',postman_report:'Unmodified official Postman CLI report: evidence/postman-run.html',note:'app-simulated-503 images use an intercepted 503 response to demonstrate the unavailable state. Other app requests reach the live API.'},null,2));
await browser.close();
console.log('Captured Postman summary, request list, health, metadata, valid and invalid responses, and live API documentation.');
