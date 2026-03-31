<?php

namespace App\Controller;

use Symfony\Bundle\FrameworkBundle\Controller\AbstractController;
use Symfony\Component\HttpFoundation\Response;
use Symfony\Component\Routing\Attribute\Route;
use Symfony\UX\Map\Bridge\Leaflet\LeafletOptions;
use Symfony\UX\Map\Bridge\Leaflet\Option\TileLayer;
use Symfony\UX\Map\Map;
use Symfony\UX\Map\Marker;
use Symfony\UX\Map\Point;

class HomeController extends AbstractController
{
    #[Route('/', name: 'app_home')]
    public function index(): Response
    {
        // TODO: replace with real DB data
        $stations = [
            [
                'lat' => 45.7534031, 'lng' => 4.8295061,
                'name' => 'Station Centre-Ville',
                'aqiColor' => '#f43f5e',
                'aqi' => 78, 'aqiLabel' => 'Malsain',
                'desc' => "Les groupes sensibles devraient limiter les efforts en extérieur. Qualité de l'air réduite par le trafic local.",
                'temp' => '22°C', 'humidity' => '45%', 'wind' => '12k/h',
                'pm25' => '12', 'no2' => '34', 'co' => '0.5',
            ],
            [
                'lat' => 48.8650, 'lng' => 2.3350,
                'name' => 'Station Parc',
                'aqiColor' => '#1ab394',
                'aqi' => 32, 'aqiLabel' => 'Bon',
                'desc' => "Qualité de l'air satisfaisante. Profitez librement des activités en extérieur.",
                'temp' => '21°C', 'humidity' => '52%', 'wind' => '8k/h',
                'pm25' => '5', 'no2' => '12', 'co' => '0.2',
            ],
            [
                'lat' => 48.8450, 'lng' => 2.3700,
                'name' => 'Zone Industrielle',
                'aqiColor' => '#fbbf24',
                'aqi' => 120, 'aqiLabel' => 'Très Malsain',
                'desc' => "Tout le monde devrait réduire les efforts prolongés en extérieur. Émissions industrielles détectées.",
                'temp' => '23°C', 'humidity' => '38%', 'wind' => '15k/h',
                'pm25' => '35', 'no2' => '58', 'co' => '1.2',
            ],
        ];

        $map = new Map('default')
            ->center(new Point(48.8566, 2.3522))
            ->zoom(13)
            ->options(new LeafletOptions()
                ->tileLayer(new TileLayer(
                    url: 'https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png',
                    attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OSM</a> &copy; <a href="https://carto.com/">CARTO</a>',
                    options: ['subdomains' => 'abcd', 'maxZoom' => 19]
                ))
            )
        ;

        foreach ($stations as $s) {
            $map->addMarker(new Marker(
                position: new Point($s['lat'], $s['lng']),
                title: $s['name'],
                extra: array_diff_key($s, array_flip(['lat', 'lng', 'name'])),
            ));
        }

        return $this->render('home/index.html.twig', [
            'map' => $map,
        ]);
    }
}
