# Use an official Node.js runtime as a parent image
FROM node:20-alpine

# Set the working directory to /app
WORKDIR /app

# Copy package files (including lockfiles) to the working directory
COPY package.json package-lock.json* ./

# Install the dependencies
RUN npm install

# Copy the rest of the application code
COPY . .

# Expose port 5173 for Vite
EXPOSE 5173

# Run the dev server and explicitly bind to all network interfaces so it's accessible from host
CMD ["npm", "run", "dev", "--", "--host"]
