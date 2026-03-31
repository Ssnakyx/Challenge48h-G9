<?php

namespace App\Controller;

use App\Entity\GeoPoint;
use App\Entity\PollutionMeasurements;
use App\Entity\WeatherMeasurements;
use App\Form\MapFilterType;
use App\Model\MapFilterData;
use App\Repository\GeoPointRepository;
use Doctrine\Common\Collections\Collection;
use Doctrine\ORM\Query\Expr\Math;
use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Request;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;
use Symfony\UX\Map\Bridge\Leaflet\LeafletOptions;
use Symfony\UX\Map\Bridge\Leaflet\Option\TileLayer;
use Symfony\UX\Map\Map;
use Symfony\UX\Map\Marker;
use Symfony\UX\Map\Point;

class HomeController extends AbstractController
{
    private const COLORS = [ // pour extra.aqiColor (0=best → 5=worst)
        "#00FF00", // green  – excellent
        "#66FF00",
        "#CCFF00",
        "#FFCC00", // yellow
        "#FF6600",
        "#FF0000", // red    – dangerous
    ];

    private const AQI_LABELS = [
        'Excellent',
        'Bon',
        'Modéré',
        'Médiocre',
        'Mauvais',
        'Dangereux',
    ];

    private const AQI_DESCS = [
        'Qualité de l\'air idéale pour toutes les activités.',
        'Qualité de l\'air acceptable.',
        'Les personnes sensibles devraient limiter les efforts prolongés.',
        'Tout le monde peut ressentir des effets sur la santé.',
        'Effets graves sur la santé pour tous.',
        'Alerte sanitaire : danger pour l\'ensemble de la population.',
    ];

    public function __construct(
        private readonly GeoPointRepository $geoPointRepository,
    ){
    }

    #[Route('/', name: 'app_home')]
    public function index(Request $request): Response
    {
        $mapFilterData = new MapFilterData();

        $form = $this->createForm(MapFilterType::class, $mapFilterData);
        $form->handleRequest($request);

        /** @var GeoPoint[] $geoPoints */
        $geoPoints = $this->geoPointRepository->findWithLatestMeasurementsByDay($mapFilterData);

        $map = new Map('default')
            ->center(new Point(46.6, 2.5))
            ->zoom(6)
            ->options(new LeafletOptions()
                ->tileLayer(new TileLayer(
                    url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>',
                    options: ['subdomains' => 'abcd', 'maxZoom' => 19]
                ))
            )
            ->minZoom(6)
        ;

        foreach ($geoPoints as $geoPoint) {
            /** @var PollutionMeasurements[] $pollMeasures */
            $pollMeasures = [];
            foreach($geoPoint->getPollutionMeasurements() as $pm) {
                $pollMeasures[] = $pm->getScore();
            }
            $pollScore = array_sum($pollMeasures) / count($pollMeasures);
            /** @var PollutionMeasurements $pollMeasure */
            $pollMeasure = $geoPoint->getPollutionMeasurements()[0];

            /** @var WeatherMeasurements[] $weatherMeasures */
            $weatherMeasures = [];
            foreach($geoPoint->getWeatherMeasurements() as $wm) {
                $weatherMeasures[] = $wm->getScore();
            }
            $weatherScore = array_sum($weatherMeasures) / count($weatherMeasures);
            $weatherMeasure = $geoPoint->getWeatherMeasurements()[0];

            $newScore = min(round((($pollScore * 10) + $weatherScore) * 10 / 2), 100);
            $bucket = min((int) floor($newScore / 100 * 5), 5);
            $colour = self::COLORS[$bucket];

            $map->addMarker(new Marker(
                position: new Point($geoPoint->getLatitude(), $geoPoint->getLongitude()),
                title: $geoPoint->getStationName(),
                extra: [
                    'aqi' => $newScore,
                    'aqiColor' => $colour,
                    'aqiLabel' => self::AQI_LABELS[$bucket],
                    'desc' => self::AQI_DESCS[$bucket],
                    'temp' => $weatherMeasure->getTemperatureReal(),
                    'humidity' => $weatherMeasure->getHumidity(),
                    'wind' => $weatherMeasure->getWindSpeed(),
                    'pm25' => $pollMeasure->getPm25Value(),
                    'no2' => $pollMeasure->getNo2Value(),
                    'co' => $pollMeasure->getCoValue(),
                ],
            ));
        }

        return $this->render('home/index.html.twig', [
            'map' => $map,
            'stationsCount' => count($geoPoints),
            'form' => $form,
        ]);
    }
}
