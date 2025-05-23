class FakeQueryGenerator:

    async def __call__(self, prompt: str, _q: str) -> str:
        return f"""
            SELECT
                obsolescence_val,
                obsolescence,
                parts_flagged,
                alert_type,
                alert_category
            FROM metrics
            WHERE id = '{_q}'
            AND date >= CURRENT_DATE - make_interval(days => :day_range);
        """