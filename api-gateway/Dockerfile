FROM node:18-alpine
WORKDIR /app
COPY package*.json ./
RUN npm install
COPY gateway.js .
EXPOSE 3000
CMD ["node", "gateway.js"]