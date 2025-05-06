# n8n-cheerio-stack

🚀 Triển khai n8n kèm theo thư viện cheerio để xử lý HTML.

## 📁 Cấu trúc

- Dockerfile: Image tùy chỉnh cài cheerio
- docker-compose.yml: Khởi tạo n8n container
- .env.template: Mẫu cấu hình biến môi trường

## ⚙️ Sử dụng

1. Tạo file `.env` từ `.env.template`
2. Chạy bằng lệnh:
   ```bash
   docker compose --env-file .env up -d
   ```

## ✅ Test cheerio trong Function Node

```javascript
const cheerio = require("cheerio");
const html = `<ul><li>Item 1</li><li>Item 2</li></ul>`;
const $ = cheerio.load(html);
const items = $('li').map((i, el) => $(el).text()).get();
return [{ json: { items } }];
```