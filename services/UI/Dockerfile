# 1) Chọn image node nhẹ
FROM node:18-alpine

WORKDIR /app

# 2) Copy manifest để cài dependencies
COPY package.json package-lock.json ./

# RUN npm ci
RUN npm install

# 4) Copy toàn bộ source React
COPY . .

# 5) Build app thành static files
RUN npm run build

# 6) Dùng serve để phục vụ thư mục dist
RUN npm install -g serve

# 7) Khởi chạy web server
CMD ["serve", "-s", "dist", "-l", "3000"]
