import json
import re
from datetime import datetime
from pathlib import Path
from typing import Any

import aiofiles

from src.core import DatasetConfig, ViewConfig, SqlStatement, DataPoint
from src.crosscutting import auto_slots, Logger
from src.infrastructure import Settings
import uuid


LOADER_SLOTS = "settings", "logger", "type", "data"

class JsonViewConfigProcessor:
    __slots__ = LOADER_SLOTS

    def __init__(self, settings: Settings, logger: Logger):
        self.logger = logger
        self.settings = settings
        self.type = ViewConfig
        self.data = []

    async def __call__(self) -> None:
        path = Path(self.settings.SEED_DATA_JSON)
        if not path.exists():
            self.logger.warning(f"No seed data file as {path.resolve()}")
            return

        async with aiofiles.open(path, 'r', encoding='utf-8') as f:
            contents = await f.read()
            data = json.loads(contents)

        layouts_by_breakpoint = data.get("datasets", {}).get("layouts", {})

        view_configs: list[ViewConfig] = []
        for breakpoint, layouts in layouts_by_breakpoint.items():
            for layout in layouts:
                view_configs.append(ViewConfig(
                    id=str(uuid.uuid4()),
                    element_id=layout["i"],
                    breakpoint=breakpoint,
                    x=layout["x"],
                    y=layout["y"],
                    w=layout["w"],
                    h=layout["h"],
                    static=layout.get("static", None)
                ))

        self.data = view_configs


class JsonDataPointProcessor:
    __slots__ = LOADER_SLOTS

    def __init__(self, settings: Settings, logger: Logger):
        self.logger = logger
        self.settings = settings
        self.type = DataPoint
        self.data = []

    async def __call__(self) -> None:
        path = Path(self.settings.SEED_DATA_JSON)
        if not path.exists():
            self.logger.warning(f"No seed data file as {path.resolve()}")
            return

        async with aiofiles.open(path, 'r', encoding='utf-8') as f:
            contents = await f.read()
            data = json.loads(contents)

        records: list[DataPoint] = []
        for record in data.get("metric_records", []):
            records.append(DataPoint(
                dataset_id=str(uuid.uuid4()),
                id=record.get("id"),
                timestamp=datetime.fromisoformat(record["timestamp"]),
                decay_value=record.get("decay_value"),
                decay_rate=record.get("decay_rate"),
                items_flagged=record.get("items_flagged"),
                notification_type=record.get("notification_type"),
                notification_category=record.get("notification_category"),
            ))

        self.data = records


class ConfigurationImporter:
    __slots__ = LOADER_SLOTS

    def __init__(self, settings: Settings, logger: Logger):
        self.logger = logger
        self.settings = settings
        self.type = DatasetConfig
        self.data = []

    async def __call__(self) -> None:
        path = Path(self.settings.SEED_DATA_JSON)
        if not path.exists():
            self.logger.warning(f"No seed data file as {path.resolve()}")
            return

        async with aiofiles.open(path, 'r', encoding='utf-8') as f:
            contents = await f.read()
            data = json.loads(contents)

        items = data.get("datasets", {}).get("items", [])

        duplicate_id_remap = {
            "53aaf9d4-04d3-43d3-9f40-6ce4a9282a5c": "1379a764-2543-45fd-a78b-8c5a65827417"
        }
        items = remap_duplicate_ids(items, "id", duplicate_id_remap)

        dataset_configs = []
        for item in items:
            dc = DatasetConfig(
                id=item["id"],
                statement_id=item.get("statementId") or item.get("statement_id"),
                is_mutable=item["isMutable"]
            )
            dataset_configs.append(dc)

        self.data = dataset_configs

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


class JsonSqlStatementProcessor:
    __slots__ = LOADER_SLOTS

    def __init__(self, settings: Settings, logger: Logger):
        self.logger = logger
        self.settings = settings
        self.type = SqlStatement
        self.data = []

    async def __call__(self) -> None:
        path = Path(self.settings.SEED_DATA_JSON)
        if not path.exists():
            self.logger.warning(f"No seed data file at {path.resolve()}")
            return

        async with aiofiles.open(path, 'r', encoding='utf-8') as f:
            contents = await f.read()
            data = json.loads(contents)

        statements = [
            SqlStatement(id=query["id"], statement=replace_dates_and_intervals(query["statement"]))
            for query in data.get("queries", [])
        ]

        self.data = statements



def replace_dates_and_intervals(sql: str) -> str:
    sql = re.sub(
        r"BETWEEN\s+'[\d]{4}-[\d]{2}-[\d]{2}'\s+AND\s+'[\d]{4}-[\d]{2}-[\d]{2}'",
        "BETWEEN :start_date AND :end_date",
        sql
    )

    sql = re.sub(
        r"INTERVAL\s+'(\d+)' DAY",
        "make_interval(days => :day_range)",
        sql
    )

    return sql