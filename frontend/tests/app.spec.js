import {test, expect} from '@playwright/test';
import {capture} from './screenshot.js';

test('live API search and fitted pipeline', async ({page}) => {
  await page.goto('/');
  await expect(page.getByText('API ready', {exact:true})).toBeVisible({timeout:90000});
  await capture(page, {path:`../evidence/screenshots/app-initial-${test.info().project.name}.png`});
  await page.getByRole('button', {name:'Python', exact:false}).click();
  const responsePromise = page.waitForResponse(r => r.url().endsWith('/search') && r.request().method() === 'POST');
  await page.getByRole('button', {name:'Decode error'}).click();
  const response = await responsePromise;
  expect(response.status()).toBe(200);
  expect(response.url()).toContain(process.env.API_BASE_URL || 'http://127.0.0.1:8000');
  await expect(page.locator('article').first()).toContainText('Missing installed module');
  await expect(page.locator('article').first()).toContainText('similarity');
  await capture(page, {path:`../evidence/screenshots/app-search-${test.info().project.name}.png`});
  await page.getByText('Inside the fitted pipeline').click();
  await expect(page.getByText('1000 entries', {exact:true})).toBeVisible();
  await expect(page.getByText('ErrorTextNormalizer', {exact:true})).toBeVisible();
  await capture(page, {path:`../evidence/screenshots/app-results-${test.info().project.name}.png`});
});

test('blank validation and no-match query', async ({page}) => {
  await page.goto('/');
  await page.getByRole('button', {name:'Decode error'}).click();
  await expect(page.getByRole('alert')).toContainText('non-whitespace');
  await capture(page, {path:`../evidence/screenshots/app-validation-${test.info().project.name}.png`});
  await page.getByLabel('Error message or traceback').fill('zxqvblrp qqqzzzyyy');
  await page.getByRole('button', {name:'Decode error'}).click();
  await expect(page.getByRole('heading', {name:'No matching vocabulary'})).toBeVisible({timeout:90000});
  await capture(page, {path:`../evidence/screenshots/app-no-match-${test.info().project.name}.png`});
});

test('unavailable API is explained', async ({page}) => {
  await page.route('**/search', route => route.fulfill({status:503, contentType:'application/json', body:JSON.stringify({detail:'unavailable'})}));
  await page.goto('/');
  await page.getByLabel('Error message or traceback').fill('KeyError');
  await page.getByRole('button', {name:'Decode error'}).click();
  await expect(page.getByRole('alert')).toContainText('search model is unavailable');
  await capture(page, {path:`../evidence/screenshots/app-simulated-503-${test.info().project.name}.png`});
});
