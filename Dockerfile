FROM cototal/php-apache:6fbed66

ENV APP_ENV=prod

COPY . /app

RUN ln -s /etc/apache2/sites-available/symfony4.conf /etc/apache2/sites-enabled/000-default.conf

RUN composer install --optimize-autoloader --no-dev && chown -R www-data:www-data /app
