import csv
import json
from pathlib import Path
from typing import Any

import aiofiles

from src.core import MetricConfiguration, LayoutItem, Query
from src.crosscutting import auto_slots, Logger
from src.infrastructure import Settings


@auto_slots
class JsonLayoutItemLoader:

    def __init__(self, settings: Settings, logger: Logger):
        self.logger = logger
        self.settings = settings

    async def __call__(self) -> list[LayoutItem]:
        path = Path(self.settings.METRICS_SEED_JSON)
        if not path.exists():
            self.logger.warning("No layouts file")
            return []

        async with aiofiles.open(path, 'r', encoding='utf-8') as f:
            contents = await f.read()
            data = json.loads(contents)

        layouts_by_breakpoint = data.get("layouts", {})

        import uuid
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

        return layout_items


@auto_slots
class JsonMetricConfigurationLoader:

    def __init__(self, settings: Settings, logger: Logger):
        self.logger = logger
        self.settings = settings

    async def __call__(self) -> list[MetricConfiguration]:
        path = Path(self.settings.METRICS_SEED_JSON)
        if not path.exists():
            self.logger.warning("No metrics file")
            return []

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

        return metric_configs

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


@auto_slots
class CsvQueryLoader:

    def __init__(self, settings: Settings, logger: Logger):
        self.logger = logger
        self.settings = settings

    async def __call__(self) -> list[Query]:
        path = Path(self.settings.QUERIES_SEED_JSON)
        if not path.exists():
            self.logger.warning("No queries file")
            return []

        async with aiofiles.open(path, 'r', encoding='utf-8') as f:
            contents = await f.read()

        lines = contents.splitlines()

        reader = csv.DictReader(lines)
        queries = [Query(id=row["id"], query=row["query"]) for row in reader]

        return queries