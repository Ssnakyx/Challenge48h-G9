<?php

namespace App\Model;

class MapFilterData
{
    public ?\DateTime $date = null;

    public function getDate(): ?\DateTime
    {
        return $this->date;
    }

    public function setDate(?\DateTime $date): self
    {
        $this->date = $date;

        return $this;
    }
}
