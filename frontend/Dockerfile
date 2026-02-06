# Development Stage
FROM node:20-alpine AS development

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm install

# Copy project files (wird durch Volume überschrieben)
COPY . .

EXPOSE 3000

CMD ["npm", "run", "dev"]

# Production Stage
FROM node:20-alpine AS production

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production

# Copy project files
COPY . .

# Build the application
RUN npm run build

EXPOSE 3000

CMD ["npm", "start"]
