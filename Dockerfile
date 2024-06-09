# Build assets
FROM node:lts AS assets

RUN mkdir /app
WORKDIR /app
COPY . /app
RUN npm install && npm run build

# Prepare server
FROM cototal/php-apache:8-0-20-202206142254-7679ada

ENV APP_ENV=prod

COPY . /app
COPY --from=assets /app/public/build /app/public/build

RUN ln -s /etc/apache2/sites-available/symfony4.conf /etc/apache2/sites-enabled/000-default.conf

RUN composer install --optimize-autoloader --no-dev && chown -R www-data:www-data /app
