<?php

namespace App\Repository;

use App\Entity\GeoPoint;
use App\Entity\WeatherMeasurements;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @extends ServiceEntityRepository<WeatherMeasurements>
 */
class WeatherMeasurementsRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, WeatherMeasurements::class);
    }
}
