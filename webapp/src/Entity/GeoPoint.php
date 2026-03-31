<?php

namespace App\Entity;

use App\Repository\GeoPointRepository;
use Doctrine\Common\Collections\ArrayCollection;
use Doctrine\Common\Collections\Collection;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: GeoPointRepository::class)]
class GeoPoint
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column(type: Types::INTEGER)]
    private ?int $id = null;

    #[ORM\Column(type: Types::STRING, length: 64, nullable: true)]
    private ?string $stationCode = null;

    #[ORM\Column(type: Types::STRING, length: 255, nullable: true)]
    private ?string $stationName = null;

    #[ORM\Column(type: Types::FLOAT, nullable: true)]
    private ?float $latitude = null;

    #[ORM\Column(type: Types::FLOAT, nullable: true)]
    private ?float $longitude = null;

    #[ORM\Column(type: Types::DATE_MUTABLE)]
    private ?\DateTime $timestamp = null;

    #[ORM\Column(type: Types::DATE_MUTABLE)]
    private ?\DateTime $date = null;

    #[ORM\Column(type: Types::DATE_MUTABLE)]
    private ?\DateTime $createdAt = null;

    /**
     * @var Collection<int, PollutionMeasurements>
     */
    #[ORM\OneToMany(targetEntity: PollutionMeasurements::class, mappedBy: 'geoPoint')]
    private Collection $pollutionMeasurements;

    /**
     * @var Collection<int, WeatherMeasurements>
     */
    #[ORM\OneToMany(targetEntity: WeatherMeasurements::class, mappedBy: 'geoPoint')]
    private Collection $weatherMeasurements;

    public function __construct()
    {
        $this->pollutionMeasurements = new ArrayCollection();
        $this->weatherMeasurements = new ArrayCollection();
    }

    public function getId(): ?int
    {
        return $this->id;
    }

    public function getStationCode(): ?string
    {
        return $this->stationCode;
    }

    public function setStationCode(string $stationCode): static
    {
        $this->stationCode = $stationCode;

        return $this;
    }

    public function getStationName(): ?string
    {
        return $this->stationName;
    }

    public function setStationName(string $stationName): static
    {
        $this->stationName = $stationName;

        return $this;
    }

    public function getLatitude(): ?float
    {
        return $this->latitude;
    }

    public function setLatitude(float $latitude): static
    {
        $this->latitude = $latitude;

        return $this;
    }

    public function getLongitude(): ?float
    {
        return $this->longitude;
    }

    public function setLongitude(float $longitude): static
    {
        $this->longitude = $longitude;

        return $this;
    }

    public function getTimestamp(): ?\DateTime
    {
        return $this->timestamp;
    }

    public function setTimestamp(?\DateTime $timestamp): static
    {
        $this->timestamp = $timestamp;

        return $this;
    }

    public function getDate(): ?\DateTime
    {
        return $this->date;
    }

    public function setDate(?\DateTime $date): static
    {
        $this->date = $date;

        return $this;
    }

    public function getCreatedAt(): ?\DateTime
    {
        return $this->createdAt;
    }

    public function setCreatedAt(?\DateTime $createdAt): static
    {
        $this->createdAt = $createdAt;

        return $this;
    }

    /**
     * @return Collection<int, PollutionMeasurements>
     */
    public function getPollutionMeasurements(): Collection
    {
        return $this->pollutionMeasurements;
    }

    public function addPollutionMeasurement(PollutionMeasurements $pollutionMeasurement): static
    {
        if (!$this->pollutionMeasurements->contains($pollutionMeasurement)) {
            $this->pollutionMeasurements->add($pollutionMeasurement);
            $pollutionMeasurement->setGeoPoint($this);
        }

        return $this;
    }

    public function removePollutionMeasurement(PollutionMeasurements $pollutionMeasurement): static
    {
        if ($this->pollutionMeasurements->removeElement($pollutionMeasurement)) {
            // set the owning side to null (unless already changed)
            if ($pollutionMeasurement->getGeoPoint() === $this) {
                $pollutionMeasurement->setGeoPoint(null);
            }
        }

        return $this;
    }

    /**
     * @return Collection<int, WeatherMeasurements>
     */
    public function getWeatherMeasurements(): Collection
    {
        return $this->weatherMeasurements;
    }

    public function addWeatherMeasurement(WeatherMeasurements $weatherMeasurement): static
    {
        if (!$this->weatherMeasurements->contains($weatherMeasurement)) {
            $this->weatherMeasurements->add($weatherMeasurement);
            $weatherMeasurement->setGeoPoint($this);
        }

        return $this;
    }

    public function removeWeatherMeasurement(WeatherMeasurements $weatherMeasurement): static
    {
        if ($this->weatherMeasurements->removeElement($weatherMeasurement)) {
            // set the owning side to null (unless already changed)
            if ($weatherMeasurement->getGeoPoint() === $this) {
                $weatherMeasurement->setGeoPoint(null);
            }
        }

        return $this;
    }
}
