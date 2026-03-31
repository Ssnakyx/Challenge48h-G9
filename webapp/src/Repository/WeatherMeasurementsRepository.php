<?php

namespace App\Repository;

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

    public function findByDate(\DateTime $date = new \DateTime()): array
    {
        return $this
            ->createQueryBuilder('wm')
            ->where('wm.date > :date')
            ->setParameter('date', $date)
            ->getQuery()
            ->getResult()
            ;
    }
}
