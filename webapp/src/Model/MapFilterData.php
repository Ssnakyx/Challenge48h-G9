<?php

namespace App\Model;

class MapFilterData
{
    public ?\DateTime $dateMin = null;
    public ?\DateTime $dateMax = null;
    public ?float $indexMin = null;
    public ?float $indexMax = null;
    public ?string $searchArea = null;

    public function getDateMin(): ?\DateTime
    {
        return $this->dateMin;
    }

    public function setDateMin(?\DateTime $dateMin): self
    {
        $this->dateMin = $dateMin;

        return $this;
    }

    public function getDateMax(): ?\DateTime
    {
        return $this->dateMax;
    }

    public function setDateMax(?\DateTime $dateMax): self
    {
        $this->dateMax = $dateMax;

        return $this;
    }

    public function getIndexMin(): ?float
    {
        return $this->indexMin;
    }

    public function setIndexMin(?float $indexMin): self
    {
        $this->indexMin = $indexMin;

        return $this;
    }

    public function getIndexMax(): ?float
    {
        return $this->indexMax;
    }

    public function setIndexMax(?float $indexMax): self
    {
        $this->indexMax = $indexMax;

        return $this;
    }

    public function getSearchArea(): ?string
    {
        return $this->searchArea;
    }

    public function setSearchArea(?string $searchArea): self
    {
        $this->searchArea = $searchArea;

        return $this;
    }
}
