<?php

namespace App\Entity;

use App\Repository\WeatherMeasurementsRepository;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: WeatherMeasurementsRepository::class)]
class WeatherMeasurements
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column(type: Types::INTEGER)]
    private ?int $id = null;

    #[ORM\Column(type: Types::INTEGER)]
    private ?int $geoPointId = null;

    #[ORM\Column(type: Types::FLOAT, nullable: true)]
    private ?float $temperatureReal = null;

    #[ORM\Column(type: Types::FLOAT, nullable: true)]
    private ?float $temperatureFeelsLike = null;

    #[ORM\Column(type: Types::FLOAT, nullable: true)]
    private ?float $humidity = null;

    #[ORM\Column(type: Types::FLOAT, nullable: true)]
    private ?float $windDirection = null;

    #[ORM\Column(type: Types::FLOAT, nullable: true)]
    private ?float $windSpeed = null;

    #[ORM\Column(type: Types::FLOAT, nullable: true)]
    private ?float $pressure = null;

    #[ORM\Column(type: Types::FLOAT, nullable: true)]
    private ?float $score = null;

    #[ORM\Column(type: Types::DATE_MUTABLE)]
    private ?\DateTime $date = null;

    #[ORM\Column(type: Types::DATE_MUTABLE)]
    private ?\DateTime $createdAt = null;

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getGeoPointId(): ?int
    {
        return $this->geoPointId;
    }

    public function setGeoPointId(int $geoPointId): static
    {
        $this->geoPointId = $geoPointId;

        return $this;
    }

    public function getTemperatureReal(): ?float
    {
        return $this->temperatureReal;
    }

    public function setTemperatureReal(?float $temperatureReal): static
    {
        $this->temperatureReal = $temperatureReal;

        return $this;
    }

    public function getTemperatureFeelsLike(): ?float
    {
        return $this->temperatureFeelsLike;
    }

    public function setTemperatureFeelsLike(?float $temperatureFeelsLike): static
    {
        $this->temperatureFeelsLike = $temperatureFeelsLike;

        return $this;
    }

    public function getHumidity(): ?float
    {
        return $this->humidity;
    }

    public function setHumidity(?float $humidity): static
    {
        $this->humidity = $humidity;

        return $this;
    }

    public function getWindDirection(): ?float
    {
        return $this->windDirection;
    }

    public function setWindDirection(?float $windDirection): static
    {
        $this->windDirection = $windDirection;

        return $this;
    }

    public function getWindSpeed(): ?float
    {
        return $this->windSpeed;
    }

    public function setWindSpeed(?float $windSpeed): static
    {
        $this->windSpeed = $windSpeed;

        return $this;
    }

    public function getPressure(): ?float
    {
        return $this->pressure;
    }

    public function setPressure(?float $pressure): static
    {
        $this->pressure = $pressure;

        return $this;
    }

    public function getScore(): ?float
    {
        return $this->score;
    }

    public function setScore(?float $score): static
    {
        $this->score = $score;

        return $this;
    }

    public function getDate(): ?\DateTime
    {
        return $this->date;
    }

    public function setDate(\DateTime $date): static
    {
        $this->date = $date;

        return $this;
    }

    public function getCreatedAt(): ?\DateTime
    {
        return $this->createdAt;
    }

    public function setCreatedAt(\DateTime $createdAt): static
    {
        $this->createdAt = $createdAt;

        return $this;
    }
}
