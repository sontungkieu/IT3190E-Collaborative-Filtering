# # 1) Chọn image node nhẹ
# FROM node:18-alpine

# WORKDIR /app

# # 2) Copy manifest để cài dependencies
# COPY package.json package-lock.json ./

# # RUN npm ci
# RUN npm install

# # 4) Copy toàn bộ source React
# COPY . .

# # 5) Build app thành static files
# RUN npm run build

# # 6) Dùng serve để phục vụ thư mục dist
# RUN npm install -g serve

# # 7) Khởi chạy web server
# CMD ["serve", "-s", "dist", "-l", "3000"]
# Multi-stage Dockerfile for React UI Service

# 1) Build stage
FROM node:18-alpine AS builder
WORKDIR /app

# Copy manifest and install dependencies
COPY package.json package-lock.json ./
RUN npm install

# Copy React source and build static files
COPY . ./
RUN npm run build

# 2) Runner stage
FROM node:18-alpine AS runner
WORKDIR /app

# Install serve globally to serve static files
RUN npm install -g serve

# Copy built files from builder stage
COPY --from=builder /app/dist ./dist

# Expose port
EXPOSE 3000

# Start server
CMD ["serve", "-s", "dist", "-l", "3000"]