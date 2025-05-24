class FakeStatementGenerator:

    async def __call__(self, prompt: str, _q: str) -> str:
        return f"""
            SELECT
                decay_value,
                decay_rate,
                items_flagged,
                notification_type,
                notification_category
            FROM data_points
            WHERE id = '{_q}'
            AND timestamp >= CURRENT_DATE - make_interval(days => :day_range);
        """