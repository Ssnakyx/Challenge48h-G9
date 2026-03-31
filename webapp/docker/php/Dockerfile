FROM php:8.4-cli-bookworm

# System packages required by PHP extensions and runtime tooling.
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
        git \
        unzip \
        libpq-dev \
        libicu-dev \
        libxml2-dev \
        zlib1g-dev \
        libonig-dev \
        pkg-config \
    && docker-php-ext-configure intl \
    && docker-php-ext-install -j"$(nproc)" \
        intl \
        mbstring \
        pdo_pgsql \
        xml \
    && rm -rf /var/lib/apt/lists/*

# Composer for dependency installation and Symfony tooling.
COPY --from=composer:2 /usr/bin/composer /usr/bin/composer

WORKDIR /app

# Install dependencies first for better layer caching.
COPY composer.json composer.lock* ./
RUN composer install --no-interaction --prefer-dist --no-scripts

# Copy source and run post-install scripts.
COPY . .
RUN composer install --no-interaction --prefer-dist

EXPOSE 8000

CMD ["php", "-S", "0.0.0.0:8000", "-t", "public"]
