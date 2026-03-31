<?php

namespace App\Repository;

use App\Entity\GeoPoint;
use App\Entity\PollutionMeasurements;
use App\Entity\WeatherMeasurements;
use Doctrine\Bundle\DoctrineBundle\Repository\ServiceEntityRepository;
use Doctrine\DBAL\Types\Types;
use Doctrine\Persistence\ManagerRegistry;

/**
 * @extends ServiceEntityRepository<GeoPoint>
 */
class GeoPointRepository extends ServiceEntityRepository
{
    public function __construct(ManagerRegistry $registry)
    {
        parent::__construct($registry, GeoPoint::class);
    }

    public function findAllGeoPoints(): array
    {
        return $this->createQueryBuilder('g')
            ->getQuery()
            ->getResult();
    }

    /**
     * Returns all GeoPoints with their latest PollutionMeasurements for the given day.
     * Uses a subquery to get MAX(id) per geoPoint on that date, avoiding N+1.
     *
     * @return GeoPoint[]
     */
    /**
     * Returns all GeoPoints with their latest PollutionMeasurements and WeatherMeasurements
     * for the given day, in a single query. Uses MAX(id) subqueries per association.
     *
     * @return GeoPoint[]
     */
    public function findWithLatestMeasurementsByDay(\DateTime $date): array
    {
        $em = $this->getEntityManager();

        $latestPollutionSubQb = $em->createQueryBuilder()
            ->select('MAX(pm2.id)')
            ->from(PollutionMeasurements::class, 'pm2')
            ->where('pm2.date = :date')
            ->groupBy('pm2.geoPoint');

        $latestWeatherSubQb = $em->createQueryBuilder()
            ->select('MAX(wm2.id)')
            ->from(WeatherMeasurements::class, 'wm2')
            ->where('wm2.date = :date')
            ->groupBy('wm2.geoPoint');

        return $this->createQueryBuilder('g')
            ->addSelect('pm', 'wm')
            ->innerJoin('g.pollutionMeasurements', 'pm')
            ->innerJoin('g.weatherMeasurements', 'wm')
            ->where('pm.id IN (' . $latestPollutionSubQb->getDQL() . ')')
            ->andWhere('wm.id IN (' . $latestWeatherSubQb->getDQL() . ')')
            ->setParameter('date', $date, Types::DATE_MUTABLE)
            ->getQuery()
            ->getResult();
    }
}
