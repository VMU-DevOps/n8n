
const { chromium } = require('playwright');
const { execSync } = require('child_process');
const readline = require('readline');
const fs = require('fs');

function ask(question) {
  const rl = readline.createInterface({
    input: process.stdin,
    output: process.stdout
  });
  return new Promise(resolve => rl.question(question, ans => {
    rl.close();
    resolve(ans);
  }));
}

(async () => {
  const browser = await chromium.launch({ headless: false });
  const page = await browser.newPage();

  console.log("🧭 Truy cập trang GDT...");
  await page.goto('https://hoadondientu.gdt.gov.vn/');

  const iframe = page.frameLocator('iframe[src*="/login"]');

  const captchaImg = iframe.locator('#imgCaptcha');
  await captchaImg.screenshot({ path: '/data/captcha.png' });
  console.log("🖼 CAPTCHA đã lưu tại: /data/captcha.png");

  const mst = await ask("🔐 Nhập Mã số thuế: ");
  const password = await ask("🔑 Nhập Mật khẩu: ");
  const captcha = await ask("🔤 Nhập mã CAPTCHA từ ảnh: ");

  await iframe.locator('#txtUserName').fill(mst);
  await iframe.locator('#txtPass').fill(password);
  await iframe.locator('#txtCaptcha').fill(captcha);

  await iframe.locator('#btnLogin').click();
  await page.waitForTimeout(8000);

  const html = await page.content();
  fs.writeFileSync('/data/dashboard.html', html);

  console.log("✅ Đã đăng nhập và lưu dashboard.html");
  await browser.close();
})();
