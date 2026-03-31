"""
Helpers that download datasets from data.gouv.fr.
"""

from __future__ import annotations

import io
import logging
import re
from datetime import datetime
from typing import Iterable, List, Optional
from xml.etree import ElementTree

import pandas as pd
import requests

from .config import Settings, get_settings

logger = logging.getLogger(__name__)

DATE_RE = re.compile(r"FR_E2_(\d{4}-\d{2}-\d{2})\.csv$")
S3_NS = {"s3": "http://s3.amazonaws.com/doc/2006-03-01/"}


class DataGouvClient:
    """Minimal client able to fetch the resources referenced in the brief."""

    def __init__(self, settings: Settings | None = None) -> None:
        self.settings = settings or get_settings()
        self.session = requests.Session()
        self.session.headers.update(
            {"User-Agent": "challenge48h-impact-index (+https://data.gouv.fr)"}
        )

    def _list_bucket_objects(
        self, prefix: str, max_keys: int = 500
    ) -> Iterable[dict[str, str]]:
        """Iterate over S3 objects under the provided prefix."""

        token: Optional[str] = None
        base_url = self.settings.pollution_bucket.rstrip("/")

        while True:
            params = {
                "list-type": "2",
                "prefix": prefix,
                "max-keys": str(max_keys),
            }
            if token:
                params["continuation-token"] = token
            response = self.session.get(base_url, params=params, timeout=60)
            response.raise_for_status()
            root = ElementTree.fromstring(response.content)
            for content in root.findall("s3:Contents", namespaces=S3_NS):
                key = content.findtext("s3:Key", default="", namespaces=S3_NS)
                last_modified = content.findtext(
                    "s3:LastModified", default="", namespaces=S3_NS
                )
                if key.endswith(".csv"):
                    yield {"key": key, "last_modified": last_modified}
            token = root.findtext("s3:NextContinuationToken", default=None, namespaces=S3_NS)
            if not token:
                break

    def _download_to_buffer(self, url: str, timeout: int = 120) -> io.BytesIO:
        response = self.session.get(url, timeout=timeout)
        response.raise_for_status()
        return io.BytesIO(response.content)

    def _load_sample_pollution(self) -> pd.DataFrame:
        logger.warning("Falling back to local sample pollution data")
        return pd.read_csv(
            self.settings.sample_pollution_path,
            sep=";",
            encoding="utf-8",
            dtype=str,
        )

    def _download_pollution_keys(self, keys: List[str]) -> pd.DataFrame:
        frames: List[pd.DataFrame] = []
        for key in keys:
            url = f"{self.settings.pollution_bucket.rstrip('/')}/{key}"
            try:
                buffer = self._download_to_buffer(url)
                df = pd.read_csv(
                    buffer,
                    sep=";",
                    encoding="latin-1",
                    dtype=str,
                )
                frames.append(df)
            except Exception as exc:  # pragma: no cover - network failure fallback
                logger.warning("Unable to download %s (%s)", key, exc)
        if not frames:
            return self._load_sample_pollution()
        return pd.concat(frames, ignore_index=True)

    def fetch_pollution_measurements(
        self,
        start_date: datetime,
        end_date: datetime,
        max_files: int = 7,
    ) -> pd.DataFrame:
        """
        Download pollution CSV files covering the requested time span.

        The files are quite large so by default we cap the number of days to ingest.
        """

        start_day = start_date.date()
        end_day = end_date.date()
        wanted_keys: List[str] = []
        for year in range(start_date.year, end_date.year + 1):
            prefix = f"{self.settings.pollution_prefix}{year}/"
            for obj in self._list_bucket_objects(prefix):
                match = DATE_RE.search(obj["key"])
                if not match:
                    continue
                file_date = datetime.fromisoformat(match.group(1)).date()
                if start_day <= file_date <= end_day:
                    wanted_keys.append(obj["key"])
        wanted_keys = sorted(wanted_keys)[-max_files:]
        logger.info("Downloading %s pollution day files", len(wanted_keys))

        if not wanted_keys:
            logger.warning("No pollution files matched requested date range.")
            return self._load_sample_pollution()
        return self._download_pollution_keys(wanted_keys)

    def fetch_latest_pollution_measurements(
        self,
        window_hours: int = 24,
    ) -> pd.DataFrame:
        """Download the most recent CSV files available (real-time mode)."""

        now = datetime.utcnow()
        candidate_years = sorted({now.year, now.year - 1})
        candidate_keys: List[str] = []
        for year in candidate_years:
            prefix = f"{self.settings.pollution_prefix}{year}/"
            candidate_keys.extend(obj["key"] for obj in self._list_bucket_objects(prefix))
        candidate_keys = sorted(candidate_keys)
        if not candidate_keys:
            logger.warning("Unable to list pollution bucket contents for realtime mode.")
            return self._load_sample_pollution()
        days_needed = max(1, int(window_hours / 24) + 1)
        wanted_keys = candidate_keys[-days_needed:]
        logger.info(
            "Realtime mode: downloading %s most recent pollution day files", len(wanted_keys)
        )
        return self._download_pollution_keys(wanted_keys)

    def fetch_station_metadata(self) -> pd.DataFrame:
        """Load the XLS metadata that exposes the GPS coordinates of each site."""

        try:
            buffer = self._download_to_buffer(self.settings.pollution_metadata_url)
            return pd.read_excel(buffer)
        except Exception as exc:  # pragma: no cover - network fallback
            logger.warning("Unable to download metadata spreadsheet (%s)", exc)
            return pd.read_csv(self.settings.sample_metadata_path)

    def fetch_weather_measurements(self) -> pd.DataFrame:
        """Download the SYNOP archive (CSV.GZ) and return it as a dataframe."""

        try:
            buffer = self._download_to_buffer(self.settings.weather_resource_url)
            return pd.read_csv(buffer, sep=";", compression="gzip", dtype=str)
        except Exception as exc:  # pragma: no cover - network fallback
            logger.warning("Unable to download weather archive (%s)", exc)
            return pd.read_csv(self.settings.sample_weather_path, sep=";", dtype=str)
