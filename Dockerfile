# Build assets
FROM node:lts AS assets

RUN mkdir /app
WORKDIR /app
COPY . /app
RUN npm install && npm run build

# Prepare server
FROM cototal/php-apache:8-0-9-202108071953-6fbed66


COPY . /app
COPY --from=assets /app/public/build /app/public/build

RUN ln -s /etc/apache2/sites-available/symfony4.conf /etc/apache2/sites-enabled/000-default.conf

RUN composer install --no-dev && chown -R www-data:www-data /app
