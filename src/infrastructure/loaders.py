import csv
import io
import json
from datetime import datetime
from pathlib import Path
from typing import Any

import aiofiles

from src.core import MetricConfiguration, LayoutItem, Query, MetricRecord
from src.crosscutting import auto_slots, Logger
from src.infrastructure import Settings
import uuid


LOADER_SLOTS = "settings", "logger", "type", "data"

class JsonLayoutItemLoader:
    __slots__ = LOADER_SLOTS

    def __init__(self, settings: Settings, logger: Logger):
        self.logger = logger
        self.settings = settings
        self.type = LayoutItem
        self.data = []

    async def __call__(self) -> None:
        path = Path(self.settings.METRICS_SEED_JSON)
        if not path.exists():
            self.logger.warning(f"No layouts file as {path.resolve()}")
            return

        async with aiofiles.open(path, 'r', encoding='utf-8') as f:
            contents = await f.read()
            data = json.loads(contents)

        layouts_by_breakpoint = data.get("layouts", {})

        layout_items: list[LayoutItem] = []
        for breakpoint, layouts in layouts_by_breakpoint.items():
            for layout in layouts:
                layout_items.append(LayoutItem(
                    id=str(uuid.uuid4()),
                    item_id=layout["i"],
                    breakpoint=breakpoint,
                    x=layout["x"],
                    y=layout["y"],
                    w=layout["w"],
                    h=layout["h"],
                    static=layout.get("static", None)
                ))

        self.data = layout_items


class JsonMetricRecordLoader:
    __slots__ = LOADER_SLOTS

    def __init__(self, settings: Settings, logger: Logger):
        self.logger = logger
        self.settings = settings
        self.type = MetricRecord
        self.data = []

    async def __call__(self) -> None:
        path = Path(self.settings.METRIC_RECORDS_SEED_JSON)
        if not path.exists():
            self.logger.warning(f"No metric records file as {path.resolve()}")
            return

        async with aiofiles.open(path, 'r', encoding='utf-8') as f:
            contents = await f.read()
            data = json.loads(contents)

        records: list[MetricRecord] = []
        for record in data:
            records.append(MetricRecord(
                metric_id=str(uuid.uuid4()),
                id=record.get("id"),
                date=datetime.fromisoformat(record["date"]),
                obsolescence_val=record.get("obsolescence_val"),
                obsolescence=record.get("obsolescence"),
                parts_flagged=record.get("parts_flagged"),
                alert_type=record.get("alert_type"),
                alert_category=record.get("alert_category"),
            ))

        self.data = records


class JsonMetricConfigurationLoader:
    __slots__ = LOADER_SLOTS

    def __init__(self, settings: Settings, logger: Logger):
        self.logger = logger
        self.settings = settings
        self.type = MetricConfiguration
        self.data = []

    async def __call__(self) -> None:
        path = Path(self.settings.METRICS_SEED_JSON)
        if not path.exists():
            self.logger.warning(f"No metrics file as {path.resolve()}")
            return

        async with aiofiles.open(path, 'r', encoding='utf-8') as f:
            contents = await f.read()
            data = json.loads(contents)

        items = data.get("items", [])

        duplicate_id_remap = {
            "53aaf9d4-04d3-43d3-9f40-6ce4a9282a5c": "1379a764-2543-45fd-a78b-8c5a65827417"
        }
        items = remap_duplicate_ids(items, "id", duplicate_id_remap)

        metric_configs = []
        for item in items:
            mc = MetricConfiguration(
                id=item["id"],
                query_id=item.get("queryId") or item.get("query_id"),
                is_editable=item["isEditable"]
            )
            metric_configs.append(mc)

        self.data = metric_configs

def remap_duplicate_ids(
    items: list[dict[str, Any]],
    id_key: str,
    remap_dict: dict[str, str]
) -> list[dict[str, Any]]:
    seen = set()
    new_items = []

    for item in items:
        current_id = item.get(id_key)
        if current_id in seen and current_id in remap_dict:
            item = item.copy()
            item[id_key] = remap_dict[current_id]
        seen.add(item[id_key])
        new_items.append(item)

    return new_items


class CsvQueryLoader:
    __slots__ = LOADER_SLOTS

    def __init__(self, settings: Settings, logger: Logger):
        self.logger = logger
        self.settings = settings
        self.type = Query
        self.data = []

    async def __call__(self) -> None:
        path = Path(self.settings.QUERIES_SEED_CSV)
        if not path.exists():
            self.logger.warning(f"No csv file at {path.resolve()}")
            return

        async with aiofiles.open(path, 'r', encoding='utf-8', newline='') as f:
            contents = await f.read()

        # Use io.StringIO to create a file-like object
        csvfile = io.StringIO(contents)

        # Let csv module handle multi-line fields properly
        reader = csv.DictReader(csvfile)

        queries = [
            Query(id=row["id"], query=row["query"]) for row in reader
        ]

        self.data = queries