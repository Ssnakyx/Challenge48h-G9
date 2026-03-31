<?php

namespace App\Model;

class MapFilterData
{
    public ?\DateTime $date = null;
    public ?float $indexMin = null;
    public ?float $indexMax = null;
    public ?string $searchArea = null;

    public function getDate(): ?\DateTime
    {
        return $this->date;
    }

    public function setDate(?\DateTime $date): self
    {
        $this->date = $date;

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
