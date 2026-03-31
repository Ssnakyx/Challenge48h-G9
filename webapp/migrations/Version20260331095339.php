<?php

declare(strict_types=1);

namespace DoctrineMigrations;

use Doctrine\DBAL\Schema\Schema;
use Doctrine\Migrations\AbstractMigration;

/**
 * Auto-generated Migration: Please modify to your needs!
 */
final class Version20260331095339 extends AbstractMigration
{
    public function getDescription(): string
    {
        return '';
    }

    public function up(Schema $schema): void
    {
        // this up() migration is auto-generated, please modify it to your needs
        $this->addSql('CREATE TEMPORARY TABLE __temp__pollution_measurements AS SELECT id, geo_point_id, pm10_value, pm10_score, pm25_value, pm25_score, no2_value, no2_score, so2_value, so2_score, o3_value, o3_score, co_value, co_score, score, date, created_at FROM pollution_measurements');
        $this->addSql('DROP TABLE pollution_measurements');
        $this->addSql('CREATE TABLE pollution_measurements (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, geo_point_id INTEGER NOT NULL, pm10_value DOUBLE PRECISION DEFAULT NULL, pm10_score DOUBLE PRECISION DEFAULT NULL, pm25_value DOUBLE PRECISION DEFAULT NULL, pm25_score DOUBLE PRECISION DEFAULT NULL, no2_value DOUBLE PRECISION DEFAULT NULL, no2_score DOUBLE PRECISION DEFAULT NULL, so2_value DOUBLE PRECISION DEFAULT NULL, so2_score DOUBLE PRECISION DEFAULT NULL, o3_value DOUBLE PRECISION DEFAULT NULL, o3_score DOUBLE PRECISION DEFAULT NULL, co_value DOUBLE PRECISION DEFAULT NULL, co_score DOUBLE PRECISION DEFAULT NULL, score DOUBLE PRECISION DEFAULT NULL, date DATE NOT NULL, created_at DATE NOT NULL, CONSTRAINT FK_B01D02982E91B903 FOREIGN KEY (geo_point_id) REFERENCES geo_point (id) NOT DEFERRABLE INITIALLY IMMEDIATE)');
        $this->addSql('INSERT INTO pollution_measurements (id, geo_point_id, pm10_value, pm10_score, pm25_value, pm25_score, no2_value, no2_score, so2_value, so2_score, o3_value, o3_score, co_value, co_score, score, date, created_at) SELECT id, geo_point_id, pm10_value, pm10_score, pm25_value, pm25_score, no2_value, no2_score, so2_value, so2_score, o3_value, o3_score, co_value, co_score, score, date, created_at FROM __temp__pollution_measurements');
        $this->addSql('DROP TABLE __temp__pollution_measurements');
        $this->addSql('CREATE INDEX IDX_B01D02982E91B903 ON pollution_measurements (geo_point_id)');
        $this->addSql('CREATE TEMPORARY TABLE __temp__weather_measurements AS SELECT id, geo_point_id, temperature_real, temperature_feels_like, humidity, wind_direction, wind_speed, pressure, score, date, created_at FROM weather_measurements');
        $this->addSql('DROP TABLE weather_measurements');
        $this->addSql('CREATE TABLE weather_measurements (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, geo_point_id INTEGER NOT NULL, temperature_real DOUBLE PRECISION DEFAULT NULL, temperature_feels_like DOUBLE PRECISION DEFAULT NULL, humidity DOUBLE PRECISION DEFAULT NULL, wind_direction DOUBLE PRECISION DEFAULT NULL, wind_speed DOUBLE PRECISION DEFAULT NULL, pressure DOUBLE PRECISION DEFAULT NULL, score DOUBLE PRECISION DEFAULT NULL, date DATE NOT NULL, created_at DATE NOT NULL, CONSTRAINT FK_7F2753EF2E91B903 FOREIGN KEY (geo_point_id) REFERENCES geo_point (id) NOT DEFERRABLE INITIALLY IMMEDIATE)');
        $this->addSql('INSERT INTO weather_measurements (id, geo_point_id, temperature_real, temperature_feels_like, humidity, wind_direction, wind_speed, pressure, score, date, created_at) SELECT id, geo_point_id, temperature_real, temperature_feels_like, humidity, wind_direction, wind_speed, pressure, score, date, created_at FROM __temp__weather_measurements');
        $this->addSql('DROP TABLE __temp__weather_measurements');
        $this->addSql('CREATE INDEX IDX_7F2753EF2E91B903 ON weather_measurements (geo_point_id)');
    }

    public function down(Schema $schema): void
    {
        // this down() migration is auto-generated, please modify it to your needs
        $this->addSql('CREATE TEMPORARY TABLE __temp__pollution_measurements AS SELECT id, geo_point_id, pm10_value, pm10_score, pm25_value, pm25_score, no2_value, no2_score, so2_value, so2_score, o3_value, o3_score, co_value, co_score, score, date, created_at FROM pollution_measurements');
        $this->addSql('DROP TABLE pollution_measurements');
        $this->addSql('CREATE TABLE pollution_measurements (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, geo_point_id INTEGER NOT NULL, pm10_value DOUBLE PRECISION DEFAULT NULL, pm10_score DOUBLE PRECISION DEFAULT NULL, pm25_value DOUBLE PRECISION DEFAULT NULL, pm25_score DOUBLE PRECISION DEFAULT NULL, no2_value DOUBLE PRECISION DEFAULT NULL, no2_score DOUBLE PRECISION DEFAULT NULL, so2_value DOUBLE PRECISION DEFAULT NULL, so2_score DOUBLE PRECISION DEFAULT NULL, o3_value DOUBLE PRECISION DEFAULT NULL, o3_score DOUBLE PRECISION DEFAULT NULL, co_value DOUBLE PRECISION DEFAULT NULL, co_score DOUBLE PRECISION DEFAULT NULL, score DOUBLE PRECISION DEFAULT NULL, date DATE NOT NULL, created_at DATE NOT NULL)');
        $this->addSql('INSERT INTO pollution_measurements (id, geo_point_id, pm10_value, pm10_score, pm25_value, pm25_score, no2_value, no2_score, so2_value, so2_score, o3_value, o3_score, co_value, co_score, score, date, created_at) SELECT id, geo_point_id, pm10_value, pm10_score, pm25_value, pm25_score, no2_value, no2_score, so2_value, so2_score, o3_value, o3_score, co_value, co_score, score, date, created_at FROM __temp__pollution_measurements');
        $this->addSql('DROP TABLE __temp__pollution_measurements');
        $this->addSql('CREATE TEMPORARY TABLE __temp__weather_measurements AS SELECT id, geo_point_id, temperature_real, temperature_feels_like, humidity, wind_direction, wind_speed, pressure, score, date, created_at FROM weather_measurements');
        $this->addSql('DROP TABLE weather_measurements');
        $this->addSql('CREATE TABLE weather_measurements (id INTEGER PRIMARY KEY AUTOINCREMENT NOT NULL, geo_point_id INTEGER NOT NULL, temperature_real DOUBLE PRECISION DEFAULT NULL, temperature_feels_like DOUBLE PRECISION DEFAULT NULL, humidity DOUBLE PRECISION DEFAULT NULL, wind_direction DOUBLE PRECISION DEFAULT NULL, wind_speed DOUBLE PRECISION DEFAULT NULL, pressure DOUBLE PRECISION DEFAULT NULL, score DOUBLE PRECISION DEFAULT NULL, date DATE NOT NULL, created_at DATE NOT NULL)');
        $this->addSql('INSERT INTO weather_measurements (id, geo_point_id, temperature_real, temperature_feels_like, humidity, wind_direction, wind_speed, pressure, score, date, created_at) SELECT id, geo_point_id, temperature_real, temperature_feels_like, humidity, wind_direction, wind_speed, pressure, score, date, created_at FROM __temp__weather_measurements');
        $this->addSql('DROP TABLE __temp__weather_measurements');
    }
}
