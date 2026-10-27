import {defineConfig, devices} from '@playwright/test';
export default defineConfig({
  testDir: './tests',
  timeout: 120000,
  workers: 2,
  use: {baseURL: process.env.FRONTEND_URL || 'http://127.0.0.1:5173', trace: 'retain-on-failure'},
  reporter: [['list'], ['html', {outputFolder: '../evidence/browser-test-report', open: 'never'}]],
  projects: [{name: 'desktop', use: {...devices['Desktop Chrome']}}, {name: 'mobile', use: {...devices['iPhone 13'], defaultBrowserType: 'chromium'}}],
});
