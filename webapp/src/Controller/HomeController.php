<?php

namespace App\Controller;

use App\Entity\GeoPoint;
use App\Repository\GeoPointRepository;
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
    public function __construct(private readonly GeoPointRepository $geoPointRepository)
    {
    }

    #[Route('/', name: 'app_home')]
    public function index(): Response
    {
        /** @var GeoPoint[] $geoPoints */
        $geoPoints = $this->geoPointRepository->findAllGeoPoints();

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


        foreach ($geoPoints as $geoPoint) {
            $score =
            $map->addMarker(new Marker(
                position: new Point($geoPoint->getLatitude(), $geoPoint->getLongitude()),
                title: $geoPoint->getStationName(),
                extra: array_diff_key(array_flip([
                    'aqi' => '',
                ])),
            ));
        }

        return $this->render('home/index.html.twig', [
            'map' => $map,
        ]);
    }
}
