<?php

namespace App\DataFixtures;

use App\Entity\GeoPoint;
use App\Entity\PollutionMeasurements;
use App\Entity\WeatherMeasurements;
use Doctrine\Bundle\FixturesBundle\Fixture;
use Doctrine\Persistence\ObjectManager;

class AppFixtures extends Fixture
{
    public function load(ObjectManager $manager): void
    {
        $now = new \DateTime('today');
        $yesterday = new \DateTime('yesterday');

        $stations = [
            // === Île-de-France ===
            [
                'code' => 'FR04143', 'name' => 'Paris Centre',
                'lat' => 48.8566, 'lng' => 2.3522,
                'pollution' => ['pm25' => 14.0, 'pm10' => 22.0, 'no2' => 38.0, 'o3' => 45.0, 'so2' => 4.0, 'co' => 0.4, 'score' => 0.35, 'date' => $now],
                'weather' => ['temperatureReal' => 18.0, 'temperatureFeelsLike' => 16.5, 'humidity' => 55.0, 'windSpeed' => 10.0, 'windDirection' => 200.0, 'pressure' => 1015.0, 'score' => 3, 'date' => $now],
            ],
            [
                'code' => 'FR04024', 'name' => 'La Défense',
                'lat' => 48.8918, 'lng' => 2.2380,
                'pollution' => ['pm25' => 18.0, 'pm10' => 28.0, 'no2' => 52.0, 'o3' => 30.0, 'so2' => 6.0, 'co' => 0.6, 'score' => 0.50, 'date' => $now],
                'weather' => ['temperatureReal' => 17.5, 'temperatureFeelsLike' => 15.0, 'humidity' => 60.0, 'windSpeed' => 14.0, 'windDirection' => 210.0, 'pressure' => 1014.0, 'score' => 4, 'date' => $now],
            ],
            [
                'code' => 'FR04326', 'name' => 'Créteil',
                'lat' => 48.7900, 'lng' => 2.4550,
                'pollution' => ['pm25' => 10.0, 'pm10' => 18.0, 'no2' => 25.0, 'o3' => 55.0, 'so2' => 3.0, 'co' => 0.3, 'score' => 0.25, 'date' => $now],
                'weather' => ['temperatureReal' => 19.0, 'temperatureFeelsLike' => 18.0, 'humidity' => 48.0, 'windSpeed' => 8.0, 'windDirection' => 180.0, 'pressure' => 1016.0, 'score' => 2, 'date' => $now],
            ],
            // === Lyon ===
            [
                'code' => 'FR02010', 'name' => 'Lyon Villeurbanne',
                'lat' => 45.7676, 'lng' => 4.8344,
                'pollution' => ['pm25' => 20.0, 'pm10' => 30.0, 'no2' => 44.0, 'o3' => 60.0, 'so2' => 5.0, 'co' => 0.5, 'score' => 0.55, 'date' => $now],
                'weather' => ['temperatureReal' => 21.0, 'temperatureFeelsLike' => 20.0, 'humidity' => 42.0, 'windSpeed' => 6.0, 'windDirection' => 150.0, 'pressure' => 1012.0, 'score' => 4, 'date' => $now],
            ],
            [
                'code' => 'FR20062', 'name' => 'Lyon Part-Dieu',
                'lat' => 45.7606, 'lng' => 4.8593,
                'pollution' => ['pm25' => 24.0, 'pm10' => 35.0, 'no2' => 55.0, 'o3' => 40.0, 'so2' => 8.0, 'co' => 0.8, 'score' => 0.65, 'date' => $now],
                'weather' => ['temperatureReal' => 22.0, 'temperatureFeelsLike' => 21.0, 'humidity' => 40.0, 'windSpeed' => 5.0, 'windDirection' => 160.0, 'pressure' => 1011.0, 'score' => 5, 'date' => $now],
            ],
            // === Marseille ===
            [
                'code' => 'FR24017', 'name' => 'Marseille Vieux-Port',
                'lat' => 43.2965, 'lng' => 5.3698,
                'pollution' => ['pm25' => 16.0, 'pm10' => 26.0, 'no2' => 30.0, 'o3' => 70.0, 'so2' => 10.0, 'co' => 0.4, 'score' => 0.45, 'date' => $now],
                'weather' => ['temperatureReal' => 24.0, 'temperatureFeelsLike' => 23.0, 'humidity' => 35.0, 'windSpeed' => 18.0, 'windDirection' => 330.0, 'pressure' => 1018.0, 'score' => 3, 'date' => $now],
            ],
            [
                'code' => 'FR24021', 'name' => 'Marseille Fos-sur-Mer',
                'lat' => 43.4300, 'lng' => 4.9500,
                'pollution' => ['pm25' => 32.0, 'pm10' => 48.0, 'no2' => 60.0, 'o3' => 50.0, 'so2' => 25.0, 'co' => 1.1, 'score' => 0.85, 'date' => $now],
                'weather' => ['temperatureReal' => 23.0, 'temperatureFeelsLike' => 22.0, 'humidity' => 38.0, 'windSpeed' => 22.0, 'windDirection' => 340.0, 'pressure' => 1017.0, 'score' => 5, 'date' => $now],
            ],
            // === Metz / Grand Est ===
            [
                'code' => 'FR01005', 'name' => 'Hayange',
                'lat' => 49.3430, 'lng' => 6.0580,
                'pollution' => ['pm25' => 22.0, 'pm10' => 32.0, 'no2' => 42.0, 'o3' => 35.0, 'so2' => 12.0, 'co' => 0.7, 'score' => 0.60, 'date' => $now],
                'weather' => ['temperatureReal' => 15.0, 'temperatureFeelsLike' => 13.0, 'humidity' => 72.0, 'windSpeed' => 12.0, 'windDirection' => 220.0, 'pressure' => 1010.0, 'score' => 4, 'date' => $now],
            ],
            [
                'code' => 'FR01011', 'name' => 'Strasbourg Centre',
                'lat' => 48.5734, 'lng' => 7.7521,
                'pollution' => ['pm25' => 15.0, 'pm10' => 24.0, 'no2' => 35.0, 'o3' => 48.0, 'so2' => 5.0, 'co' => 0.4, 'score' => 0.38, 'date' => $now],
                'weather' => ['temperatureReal' => 16.0, 'temperatureFeelsLike' => 14.0, 'humidity' => 65.0, 'windSpeed' => 9.0, 'windDirection' => 190.0, 'pressure' => 1013.0, 'score' => 3, 'date' => $now],
            ],
            // === Toulouse ===
            [
                'code' => 'FR12030', 'name' => 'Toulouse Périphérique',
                'lat' => 43.6047, 'lng' => 1.4442,
                'pollution' => ['pm25' => 11.0, 'pm10' => 19.0, 'no2' => 28.0, 'o3' => 58.0, 'so2' => 3.0, 'co' => 0.3, 'score' => 0.28, 'date' => $now],
                'weather' => ['temperatureReal' => 22.0, 'temperatureFeelsLike' => 21.0, 'humidity' => 50.0, 'windSpeed' => 7.0, 'windDirection' => 270.0, 'pressure' => 1016.0, 'score' => 2, 'date' => $now],
            ],
            // === Nantes ===
            [
                'code' => 'FR23087', 'name' => 'Nantes Victor Hugo',
                'lat' => 47.2184, 'lng' => -1.5536,
                'pollution' => ['pm25' => 8.0, 'pm10' => 15.0, 'no2' => 22.0, 'o3' => 40.0, 'so2' => 2.0, 'co' => 0.2, 'score' => 0.18, 'date' => $now],
                'weather' => ['temperatureReal' => 17.0, 'temperatureFeelsLike' => 15.0, 'humidity' => 68.0, 'windSpeed' => 15.0, 'windDirection' => 250.0, 'pressure' => 1014.0, 'score' => 2, 'date' => $now],
            ],
            // === Lille ===
            [
                'code' => 'FR05022', 'name' => 'Lille Fives',
                'lat' => 50.6292, 'lng' => 3.0573,
                'pollution' => ['pm25' => 26.0, 'pm10' => 38.0, 'no2' => 48.0, 'o3' => 28.0, 'so2' => 9.0, 'co' => 0.9, 'score' => 0.70, 'date' => $now],
                'weather' => ['temperatureReal' => 14.0, 'temperatureFeelsLike' => 11.0, 'humidity' => 78.0, 'windSpeed' => 20.0, 'windDirection' => 240.0, 'pressure' => 1008.0, 'score' => 5, 'date' => $now],
            ],
            // === Bordeaux ===
            [
                'code' => 'FR31002', 'name' => 'Bordeaux Gambetta',
                'lat' => 44.8378, 'lng' => -0.5792,
                'pollution' => ['pm25' => 9.0, 'pm10' => 16.0, 'no2' => 24.0, 'o3' => 52.0, 'so2' => 3.0, 'co' => 0.3, 'score' => 0.22, 'date' => $now],
                'weather' => ['temperatureReal' => 20.0, 'temperatureFeelsLike' => 19.0, 'humidity' => 55.0, 'windSpeed' => 10.0, 'windDirection' => 260.0, 'pressure' => 1015.0, 'score' => 2, 'date' => $now],
            ],
            // === Nice ===
            [
                'code' => 'FR24033', 'name' => 'Nice Promenade',
                'lat' => 43.6961, 'lng' => 7.2660,
                'pollution' => ['pm25' => 13.0, 'pm10' => 21.0, 'no2' => 32.0, 'o3' => 65.0, 'so2' => 4.0, 'co' => 0.4, 'score' => 0.32, 'date' => $now],
                'weather' => ['temperatureReal' => 20.0, 'temperatureFeelsLike' => 19.0, 'humidity' => 45.0, 'windSpeed' => 8.0, 'windDirection' => 180.0, 'pressure' => 1019.0, 'score' => 2, 'date' => $now],
            ],
            // === Rennes ===
            [
                'code' => 'FR09101', 'name' => 'Rennes Laënnec',
                'lat' => 48.1173, 'lng' => -1.6778,
                'pollution' => ['pm25' => 7.0, 'pm10' => 13.0, 'no2' => 20.0, 'o3' => 42.0, 'so2' => 2.0, 'co' => 0.2, 'score' => 0.15, 'date' => $now],
                'weather' => ['temperatureReal' => 16.0, 'temperatureFeelsLike' => 14.0, 'humidity' => 70.0, 'windSpeed' => 12.0, 'windDirection' => 230.0, 'pressure' => 1013.0, 'score' => 2, 'date' => $now],
            ],
            // === Grenoble (Zone industrielle - pollué) ===
            [
                'code' => 'FR33120', 'name' => 'Grenoble Les Frênes',
                'lat' => 45.1885, 'lng' => 5.7245,
                'pollution' => ['pm25' => 35.0, 'pm10' => 50.0, 'no2' => 58.0, 'o3' => 25.0, 'so2' => 15.0, 'co' => 1.3, 'score' => 0.90, 'date' => $now],
                'weather' => ['temperatureReal' => 19.0, 'temperatureFeelsLike' => 18.0, 'humidity' => 50.0, 'windSpeed' => 3.0, 'windDirection' => 90.0, 'pressure' => 1009.0, 'score' => 6, 'date' => $now],
            ],
            // === Données d'hier (pour tester le filtre par date) ===
            [
                'code' => 'FR04143', 'name' => 'Paris Centre',
                'lat' => 48.8566, 'lng' => 2.3522,
                'pollution' => ['pm25' => 18.0, 'pm10' => 28.0, 'no2' => 42.0, 'o3' => 50.0, 'so2' => 5.0, 'co' => 0.5, 'score' => 0.45, 'date' => $yesterday],
                'weather' => ['temperatureReal' => 16.0, 'temperatureFeelsLike' => 14.0, 'humidity' => 62.0, 'windSpeed' => 15.0, 'windDirection' => 190.0, 'pressure' => 1012.0, 'score' => 4, 'date' => $yesterday],
            ],
            [
                'code' => 'FR02010', 'name' => 'Lyon Villeurbanne',
                'lat' => 45.7676, 'lng' => 4.8344,
                'pollution' => ['pm25' => 25.0, 'pm10' => 36.0, 'no2' => 50.0, 'o3' => 55.0, 'so2' => 7.0, 'co' => 0.7, 'score' => 0.62, 'date' => $yesterday],
                'weather' => ['temperatureReal' => 19.0, 'temperatureFeelsLike' => 17.0, 'humidity' => 48.0, 'windSpeed' => 8.0, 'windDirection' => 140.0, 'pressure' => 1010.0, 'score' => 5, 'date' => $yesterday],
            ],
        ];

        foreach ($stations as $data) {
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
                ->setGeoPoint($geoPoint)
                ->setPm10Value($p['pm10'] ?? null)
                ->setPm25Value($p['pm25'])
                ->setNo2Value($p['no2'])
                ->setSo2Value($p['so2'] ?? null)
                ->setO3Value($p['o3'] ?? null)
                ->setCoValue($p['co'])
                ->setScore($p['score'])
                ->setDate($p['date'])
                ->setCreatedAt($now);

            $manager->persist($pollution);

            $w = $data['weather'];
            $weather = (new WeatherMeasurements())
                ->setGeoPoint($geoPoint)
                ->setTemperatureReal($w['temperatureReal'])
                ->setTemperatureFeelsLike($w['temperatureFeelsLike'])
                ->setHumidity($w['humidity'])
                ->setWindSpeed($w['windSpeed'])
                ->setWindDirection($w['windDirection'])
                ->setPressure($w['pressure'])
                ->setScore($w['score'])
                ->setDate($w['date'])
                ->setCreatedAt($now);

            $manager->persist($weather);
        }

        $manager->flush();
    }
}
