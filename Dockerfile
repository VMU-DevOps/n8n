
FROM mcr.microsoft.com/playwright:v1.43.1-jammy

WORKDIR /app
COPY . /app

RUN npm install playwright

CMD ["node", "login_gdt.js"]
