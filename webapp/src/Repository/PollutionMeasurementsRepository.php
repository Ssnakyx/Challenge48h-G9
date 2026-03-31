<?php

namespace App\Repository;

use App\Entity\GeoPoint;
use App\Entity\PollutionMeasurements;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @extends ServiceEntityRepository<PollutionMeasurements>
 */
class PollutionMeasurementsRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, PollutionMeasurements::class);
    }

    public function findByDateForGeoPoint(GeoPoint $geoPoint, \DateTime $date = new \DateTime()): array
    {
        return $this
            ->createQueryBuilder('pm')
            ->andWhere('pm.date > :date')
            ->andWhere('pm.geoPoint = :geoPoint')
            ->setParameter('date', $date)
            ->setParameter('geoPoint', $geoPoint)
            ->getQuery()
            ->getResult()
        ;
    }
}
