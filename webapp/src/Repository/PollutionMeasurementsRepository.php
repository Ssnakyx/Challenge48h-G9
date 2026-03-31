<?php

namespace App\Repository;

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

    public function findByDate(\DateTime $date = new \DateTime()): array
    {
        return $this
            ->createQueryBuilder('pm')
            ->where('pm.date > :date')
            ->setParameter('date', $date)
            ->getQuery()
            ->getResult()
        ;
    }
}
