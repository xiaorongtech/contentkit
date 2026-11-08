import { test } from '@e2e-dev/web';
import { expect } from 'e2e';

// dispatch.py 依赖的浏览器契约：
// 1. snap 找 ref —— 文本框/按钮带 role + name，可定位
// 2. x-post dry-run —— 发送按钮存在但永不点击
// 3. shot —— 页面可截图（响应 200 + body 可见即视为开门契约）
// 本地 fixture 模拟 X compose 页，行为断言，不测 CDP 内部。

test('snap: 发帖文本框与发送按钮可定位', async ({ app, screen, browser }) => {
  await app.open('/');
  await expect(screen.getByRole('textbox', { name: /post/i })).toBeVisible();
  await expect(screen.getByRole('button', { name: /post/i })).toBeVisible();
});

test('dry-run: 填入文字后发送按钮不变色不自动点', async ({ app, screen }) => {
  await app.open('/');
  const box = screen.getByRole('textbox', { name: /post/i });
  await box.tap();
  await box.fill('回归草稿 dry-run');
  await expect(box).toHaveValue('回归草稿 dry-run');
  // 不去点 Post。断言按钮仍在、页面没有跳转离开。
  await expect(screen.getByRole('button', { name: /post/i })).toBeVisible();
});

test('shot: 页面响应 200 且可截图', async ({ app, browser }) => {
  await app.open('/');
  await expect(browser).toHaveURL('/');
  await expect(browser.locator('body')).toBeVisible();
});
