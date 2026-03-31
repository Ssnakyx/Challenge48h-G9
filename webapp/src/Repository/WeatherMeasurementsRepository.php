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

    public function findByDateForGeoPoint(GeoPoint $geoPoint, \DateTime $date = new \DateTime()): array
    {
        return $this
            ->createQueryBuilder('wm')
            ->andWhere('wm.date > :date')
            ->andWhere('wm.geoPoint = :geoPoint')
            ->setParameter('date', $date)
            ->setParameter('geoPoint', $geoPoint)
            ->getQuery()
            ->getResult()
            ;
    }
}
