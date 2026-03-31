<?php

namespace App\DataFixtures;

use App\Entity\GeoPoint;
use App\Entity\PollutionMeasurements;
use App\Entity\WeatherMeasurements;
use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;

class AppFixtures extends Fixture
{
    private const STATIONS = [
        [
            'code'      => 'FR-CDV',
            'name'      => 'Station Centre-Ville',
            'lat'       => 48.8566,
            'lng'       => 2.3522,
            'pollution' => [
                'pm25'  => 12.0,
                'no2'   => 34.0,
                'co'    => 0.5,
                'score' => 78.0,
            ],
            'weather'   => [
                'temperatureReal'      => 22.0,
                'temperatureFeelsLike' => 21.0,
                'humidity'             => 45.0,
                'windSpeed'            => 12.0,
                'windDirection'        => 180.0,
                'pressure'             => 1013.0,
                'score'                => 72.0,
            ],
        ],
        [
            'code'      => 'FR-PRC',
            'name'      => 'Station Parc',
            'lat'       => 48.8650,
            'lng'       => 2.3350,
            'pollution' => [
                'pm25'  => 5.0,
                'no2'   => 12.0,
                'co'    => 0.2,
                'score' => 32.0,
            ],
            'weather'   => [
                'temperatureReal'      => 21.0,
                'temperatureFeelsLike' => 20.0,
                'humidity'             => 52.0,
                'windSpeed'            => 8.0,
                'windDirection'        => 220.0,
                'pressure'             => 1015.0,
                'score'                => 85.0,
            ],
        ],
        [
            'code'      => 'FR-ZIN',
            'name'      => 'Zone Industrielle',
            'lat'       => 48.8450,
            'lng'       => 2.3700,
            'pollution' => [
                'pm25'  => 35.0,
                'no2'   => 58.0,
                'co'    => 1.2,
                'score' => 120.0,
            ],
            'weather'   => [
                'temperatureReal'      => 23.0,
                'temperatureFeelsLike' => 22.0,
                'humidity'             => 38.0,
                'windSpeed'            => 15.0,
                'windDirection'        => 270.0,
                'pressure'             => 1010.0,
                'score'                => 60.0,
            ],
        ],
    ];

    public function load(ObjectManager $manager): void
    {
        $now = new \DateTime();

        foreach (self::STATIONS as $data) {
            $geoPoint = (new GeoPoint())
                ->setStationCode($data['code'])
                ->setStationName($data['name'])
                ->setLatitude($data['lat'])
                ->setLongitude($data['lng'])
                ->setTimestamp($now)
                ->setDate($now)
                ->setCreatedAt($now);

            $manager->persist($geoPoint);
            $manager->flush(); // flush to get the generated ID

            $p = $data['pollution'];
            $pollution = (new PollutionMeasurements())
                ->setGeoPointId($geoPoint->getId())
                ->setPm25Value($p['pm25'])
                ->setNo2Value($p['no2'])
                ->setCoValue($p['co'])
                ->setScore($p['score'])
                ->setDate($now)
                ->setCreatedAt($now);

            $manager->persist($pollution);

            $w = $data['weather'];
            $weather = (new WeatherMeasurements())
                ->setGeoPointId($geoPoint->getId())
                ->setTemperatureReal($w['temperatureReal'])
                ->setTemperatureFeelsLike($w['temperatureFeelsLike'])
                ->setHumidity($w['humidity'])
                ->setWindSpeed($w['windSpeed'])
                ->setWindDirection($w['windDirection'])
                ->setPressure($w['pressure'])
                ->setScore($w['score'])
                ->setDate($now)
                ->setCreatedAt($now);

            $manager->persist($weather);
        }

        $manager->flush();
    }
}
