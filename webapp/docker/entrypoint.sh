#!/bin/sh
set -e

cd /var/www/webapp

composer install --no-dev --optimize-autoloader --no-interaction
php bin/console importmap:install --no-interaction
php bin/console assets:install --no-interaction
php bin/console cache:clear --no-interaction
php bin/console cache:warmup --no-interaction
php bin/console doctrine:migrations:migrate --no-interaction

# Fix permissions before starting Apache (entrypoint runs as root, creates root-owned dirs)
chown -R www-data:www-data /var/www/webapp/var

exec apache2-foreground
