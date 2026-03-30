<?php

namespace App\Entity;

use App\Repository\PollutionMeasurementsRepository;
use Doctrine\DBAL\Types\Types;
use Doctrine\ORM\Mapping as ORM;

#[ORM\Entity(repositoryClass: PollutionMeasurementsRepository::class)]
class PollutionMeasurements
{
    #[ORM\Id]
    #[ORM\GeneratedValue]
    #[ORM\Column(type: Types::INTEGER)]
    private ?int $id = null;

    #[ORM\Column(type: Types::INTEGER)]
    private ?int $geoPointId = null;

    #[ORM\Column(type: Types::FLOAT, nullable: true)]
    private ?float $pm10Value = null;

    #[ORM\Column(type: Types::FLOAT, nullable: true)]
    private ?float $pm10Score = null;

    #[ORM\Column(type: Types::FLOAT, nullable: true)]
    private ?float $pm25Value = null;

    #[ORM\Column(type: Types::FLOAT, nullable: true)]
    private ?float $pm25Score = null;

    #[ORM\Column(type: Types::FLOAT, nullable: true)]
    private ?float $no2Value = null;

    #[ORM\Column(type: Types::FLOAT, nullable: true)]
    private ?float $no2Score = null;

    #[ORM\Column(type: Types::FLOAT, nullable: true)]
    private ?float $so2Value = null;

    #[ORM\Column(type: Types::FLOAT, nullable: true)]
    private ?float $so2Score = null;

    #[ORM\Column(type: Types::FLOAT, nullable: true)]
    private ?float $o3Value = null;

    #[ORM\Column(type: Types::FLOAT, nullable: true)]
    private ?float $o3Score = null;

    #[ORM\Column(type: Types::FLOAT, nullable: true)]
    private ?float $coValue = null;

    #[ORM\Column(type: Types::FLOAT, nullable: true)]
    private ?float $coScore = null;

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

    public function getPm10Value(): ?float
    {
        return $this->pm10Value;
    }

    public function setPm10Value(?float $pm10Value): static
    {
        $this->pm10Value = $pm10Value;

        return $this;
    }

    public function getPm10Score(): ?float
    {
        return $this->pm10Score;
    }

    public function setPm10Score(?float $pm10Score): static
    {
        $this->pm10Score = $pm10Score;

        return $this;
    }

    public function getPm25Value(): ?float
    {
        return $this->pm25Value;
    }

    public function setPm25Value(?float $pm25Value): static
    {
        $this->pm25Value = $pm25Value;

        return $this;
    }

    public function getPm25Score(): ?float
    {
        return $this->pm25Score;
    }

    public function setPm25Score(?float $pm25Score): static
    {
        $this->pm25Score = $pm25Score;

        return $this;
    }

    public function getNo2Value(): ?float
    {
        return $this->no2Value;
    }

    public function setNo2Value(?float $no2Value): static
    {
        $this->no2Value = $no2Value;

        return $this;
    }

    public function getNo2Score(): ?float
    {
        return $this->no2Score;
    }

    public function setNo2Score(?float $no2Score): static
    {
        $this->no2Score = $no2Score;

        return $this;
    }

    public function getSo2Value(): ?float
    {
        return $this->so2Value;
    }

    public function setSo2Value(?float $so2Value): static
    {
        $this->so2Value = $so2Value;

        return $this;
    }

    public function getSo2Score(): ?float
    {
        return $this->so2Score;
    }

    public function setSo2Score(?float $so2Score): static
    {
        $this->so2Score = $so2Score;

        return $this;
    }

    public function getO3Value(): ?float
    {
        return $this->o3Value;
    }

    public function setO3Value(?float $o3Value): static
    {
        $this->o3Value = $o3Value;

        return $this;
    }

    public function getO3Score(): ?float
    {
        return $this->o3Score;
    }

    public function setO3Score(?float $o3Score): static
    {
        $this->o3Score = $o3Score;

        return $this;
    }

    public function getCoValue(): ?float
    {
        return $this->coValue;
    }

    public function setCoValue(?float $coValue): static
    {
        $this->coValue = $coValue;

        return $this;
    }

    public function getCoScore(): ?float
    {
        return $this->coScore;
    }

    public function setCoScore(?float $coScore): static
    {
        $this->coScore = $coScore;

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
