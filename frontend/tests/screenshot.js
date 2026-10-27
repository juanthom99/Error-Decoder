// Capture the whole layout at a fixed width without cutting off fixed ambient
// backgrounds or placing a sticky header midway through a full-page image.
export async function capture(page, options) {
  const viewport = page.viewportSize();
  const height = await page.evaluate(() => document.documentElement.scrollHeight);
  await page.setViewportSize({width:viewport.width, height:Math.max(viewport.height,height)});
  await page.evaluate(() => window.scrollTo(0,0));
  await page.screenshot({...options, fullPage:true, animations:'disabled'});
  await page.setViewportSize(viewport);
}
