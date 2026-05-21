# Imagen base en node ligero
FROM node:22-alpine

# Directorio de trabajo 
WORKDIR /app

# Instalar dependencias
COPY package*.json ./
RUN npm install

# Añadir ng al PATH
ENV PATH="/app/node_modules/.bin:${PATH}"

# Copiar codigo
COPY . .

# Arrancar servidor
CMD ["ng", "serve", "--host", "0.0.0.0", "--port", "4200"]
