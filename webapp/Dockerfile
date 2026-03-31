# ============================================================================
# Stage 1: Builder - Install PHP dependencies via Composer
# ============================================================================
FROM composer:2 AS builder

WORKDIR /app

# Copy only composer files for dependency resolution (cache optimization)
COPY composer.json composer.lock ./

# Install PHP dependencies without scripts (we'll run them in final stage)
RUN composer install \
    --no-dev \
    --ignore-platform-reqs \
    --no-scripts \
    --optimize-autoloader \
    --no-interaction

# ============================================================================
# Stage 2: Final - Production PHP+Apache Runtime
# ============================================================================
FROM php:8.4-apache

ENV APACHE_DOCUMENT_ROOT=/var/www/webapp/public \
    COMPOSER_ALLOW_SUPERUSER=1

WORKDIR /var/www/webapp

# Configure Apache document root and install system libs + required PHP extensions
RUN sed -ri "s!/var/www/html!${APACHE_DOCUMENT_ROOT}!g" /etc/apache2/sites-available/000-default.conf \
    && sed -ri "s!/var/www/!${APACHE_DOCUMENT_ROOT}!g" /etc/apache2/apache2.conf /etc/apache2/conf-available/*.conf \
    && a2enmod rewrite \
    && apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
        unzip \
        libicu-dev \
        libpq-dev \
    && docker-php-ext-configure intl \
    && docker-php-ext-install -j"$(nproc)" intl pdo_pgsql \
    && rm -rf /var/lib/apt/lists/*

# Install Composer in final stage
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

# Copy pre-built vendor from builder stage
COPY --from=builder /app/vendor /var/www/webapp/vendor

# Copy application sources
COPY . /var/www/webapp

# Fix permissions: chown entire directory to www-data, then create writable cache dirs
RUN chown -R www-data:www-data /var/www/webapp \
    && chmod -R 755 /var/www/webapp \
    && rm -rf /var/www/webapp/var/cache /var/www/webapp/var/log \
    && mkdir -p /var/www/webapp/var/cache /var/www/webapp/var/log \
    && chown -R www-data:www-data /var/www/webapp/var \
    && chmod -R 777 /var/www/webapp/var

# Copy and set up entrypoint script
COPY docker/entrypoint.sh /usr/local/bin/webapp-entrypoint.sh
RUN chmod +x /usr/local/bin/webapp-entrypoint.sh

ENTRYPOINT ["/usr/local/bin/webapp-entrypoint.sh"]
CMD ["apache2-foreground"]
