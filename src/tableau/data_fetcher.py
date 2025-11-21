import csv
import io
from typing import List, Dict, Any, Optional

from src.utils.logger import logger


class DataFetcher:
    """
    Pobiera dane z Tableau Cloud i buduje strukturę dashboardów/arkuszy
    z metrykami i (opcjonalnie) metadanymi.

    Działa na WSZYSTKICH views (sheets + dashboards) – Opcja 2.
    """

    def __init__(self, rest_client, metadata_client=None):
        """
        :param rest_client: TableauRestClient
        :param metadata_client: TableauMetadataClient (opcjonalnie)
        """
        self.rest = rest_client
        self.meta = metadata_client

    # ------------------------------------------------------------------
    # GŁÓWNA METODA – używana w test_tableau_api.py
    # ------------------------------------------------------------------
    def fetch_all_dashboard_metrics(self) -> List[Dict[str, Any]]:
        """
        End-to-end:
        - pobiera wszystkie views z REST API
        - dla każdego pobiera CSV summary
        - parsuje metryki z CSV
        - (opcjonalnie) dociąga metadane GraphQL
        - zwraca listę dashboardów (views) ze strukturą C
        """
        logger.info("📥 Fetching dashboards & metric data from Tableau Cloud...")

        views = self.rest.get_views()
        if not isinstance(views, list):
            logger.error("❌ get_views() did not return a list.")
            return []

        dashboards: List[Dict[str, Any]] = []

        for view in views:
            name = view.get("name") or "<unnamed>"
            view_id = view.get("id")
            logger.info(f"🔎 Fetching data for dashboard: {name}")

            if not view_id:
                logger.warning(f"⚠️ View '{name}' has no ID – skipping.")
                continue

            # REST: pobierz CSV summary (tekst)
            summary_text = self.rest.get_view_data(view_id)
            if not summary_text:
                logger.warning(f"⚠️ No summary data for '{name}'.")
                continue

            dashboard_entry = self._build_dashboard_entry(view, summary_text)

            if dashboard_entry:
                dashboards.append(dashboard_entry)
            else:
                logger.warning(f"⚠️ Could not extract metrics for '{name}'.")

        logger.info(f"✅ Successfully built {len(dashboards)} dashboards from Tableau data.")
        return dashboards

    # ------------------------------------------------------------------
    # BUDOWANIE POJEDYNCZEGO DASHBOARDU
    # ------------------------------------------------------------------
    def _build_dashboard_entry(self, view: Dict[str, Any], csv_text: str) -> Optional[Dict[str, Any]]:
        """
        Buduje pojedynczy obiekt dashboardu / widoku:
        - dashboard (nazwa)
        - view_id, url
        - metrics (dict: metric_name -> list[float])
        - expected_ranges (puste – można uzupełnić później)
        - metadata (opcjonalnie z GraphQL)
        """
        metrics = self._parse_metrics_from_csv(csv_text)
        if not metrics:
            logger.error("❌ Invalid Tableau summary format.")
            return None

        entry: Dict[str, Any] = {
            "dashboard": view.get("name"),
            "view_id": view.get("id"),
            "view_url": view.get("contentUrl"),
            "metrics": metrics,
            "expected_ranges": {},
        }

        # ENTERPRISE: dołącz metadane, jeśli metadata_client działa
        if self.meta is not None and getattr(self.meta, "enabled", False):
            try:
                md = self.meta.get_view_metadata(view.get("id"))
                if md:
                    entry["metadata"] = md
            except Exception as e:
                logger.error(f"❌ Error while fetching metadata for view {view.get('id')}: {e}")

        return entry

    # ------------------------------------------------------------------
    # PARSER CSV → METRYKI
    # ------------------------------------------------------------------
    def _parse_metrics_from_csv(self, csv_text: str) -> Optional[Dict[str, List[float]]]:
        """
        Bardzo liberalny parser:
        - Czyta CSV przez DictReader.
        - Ignoruje kolumny wymiarów (Country, State, Latitude, Longitude itd.).
        - Dla każdej kolumny próbuje parsować wartości liczbowe (w tym %).
        - Jeśli znajdzie choć jedną kolumnę z liczbami – zwraca metrics dict.
        """

        try:
            reader = csv.DictReader(io.StringIO(csv_text))
        except Exception as e:
            logger.error(f"❌ Could not read CSV summary: {e}")
            return None

        rows = list(reader)
        if not rows:
            logger.warning("⚠️ CSV summary is empty.")
            return None

        # Typowe nazwy kolumn wymiarów – ignorujemy je
        dimension_candidates = {
            "country",
            "country/region",
            "state",
            "state/province",
            "province",
            "region",
            "city",
            "latitude",
            "latitude (generated)",
            "longitude",
            "longitude (generated)",
        }

        numeric_columns: Dict[str, List[float]] = {}

        for row in rows:
            for col_name, raw_value in row.items():
                if col_name is None:
                    continue

                name = col_name.strip()
                if not name:
                    continue

                lower_name = name.lower()
                if lower_name in dimension_candidates:
                    # To wygląda na wymiar geograficzny / opisowy
                    continue

                if raw_value is None:
                    continue

                value_str = str(raw_value).strip()
                if not value_str:
                    continue

                # Normalizacja liczby:
                # - usuwamy przecinki (1,234 -> 1234)
                # - usuwamy końcówkę % (19.5% -> 19.5)
                normalized = value_str.replace(",", "")
                if normalized.endswith("%"):
                    normalized = normalized[:-1]

                try:
                    number = float(normalized)
                except ValueError:
                    # Nie udało się sparsować do float – traktujemy jako tekst / kategorię
                    continue

                numeric_columns.setdefault(name, []).append(number)

        if not numeric_columns:
            # Żadna kolumna nie okazała się liczbowa
            return None

        return numeric_columns