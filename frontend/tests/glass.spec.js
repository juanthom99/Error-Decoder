import {test, expect} from '@playwright/test';
import {capture} from './screenshot.js';

test('glass matches control supports keyboard and changes the live request', async ({page}) => {
  await page.goto('/');
  const select = page.getByRole('combobox', {name:'Matches'});
  await select.focus();
  await page.keyboard.press('ArrowDown');
  await expect(page.getByRole('option', {name:'3', exact:true})).toBeFocused();
  await page.keyboard.press('End');
  await page.keyboard.press('Enter');
  await expect(select).toContainText('5');
  await expect(select).toBeFocused();
  await select.click();
  await page.keyboard.press('Escape');
  await expect(select).toHaveAttribute('aria-expanded','false');
  await select.click();
  await page.getByRole('heading', {level:1}).click();
  await expect(select).toHaveAttribute('aria-expanded','false');
  await select.click();
  await capture(page, {path:`../evidence/screenshots/glass-dropdown-${test.info().project.name}.png`});
  await page.getByRole('option', {name:'5',exact:false}).click();
  await page.getByLabel('Error message or traceback').fill('ValueError');
  const pending=page.waitForResponse(r=>r.url().endsWith('/search')&&r.request().method()==='POST');
  await page.getByRole('button',{name:'Decode error'}).click();
  const response=await pending;
  expect(response.request().postDataJSON().top_k).toBe(5);
  expect(response.status()).toBe(200);
  await expect(page.locator('article')).toHaveCount(5);
});

test('glass layout fits the viewport and honors reduced motion', async ({page}) => {
  await page.emulateMedia({reducedMotion:'reduce'});
  await page.goto('/');
  expect(await page.locator('.orb-blue').evaluate(e=>getComputedStyle(e).animationName)).toBe('none');
  expect(await page.evaluate(()=>document.documentElement.scrollWidth <= innerWidth)).toBe(true);
  await page.getByText('Inside the fitted pipeline').click();
  await expect(page.locator('details')).toHaveAttribute('open','');
  await page.getByText('Inside the fitted pipeline').click();
  await expect(page.locator('details')).not.toHaveAttribute('open','');
});

test('expanded corpus results fit narrow phones and tablet widths', async ({page}) => {
  await page.goto('/');
  await page.getByLabel('Error message or traceback').fill('FastAPI huge integer identifier loses precision in JavaScript browser');
  await page.getByRole('button', {name:'Decode error'}).click();
  await expect(page.locator('article').first()).toContainText('Response integer outside JavaScript safe range', {timeout:90000});
  await page.getByText('Inside the fitted pipeline').click();
  await expect(page.getByText('1000 entries', {exact:true})).toBeVisible();
  const original = page.viewportSize();
  for (const width of [320, 375, 390, 768]) {
    await page.setViewportSize({width, height:844});
    expect(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth)).toBe(true);
    for (const selector of ['.primary', '.matches-trigger', '.result', '.pipeline']) {
      const boxes = await page.locator(selector).evaluateAll(elements => elements.map(el => {const r=el.getBoundingClientRect(); return {left:r.left, right:r.right};}));
      expect(boxes.every(box => box.left >= 0 && box.right <= width)).toBe(true);
    }
    if (width === 390) await capture(page, {path:`../evidence/screenshots/expanded-corpus-phone-${test.info().project.name}.png`});
  }
  await page.setViewportSize(original);
});
