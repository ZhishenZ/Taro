from pathlib import Path

filepath = Path(__file__)
Taro_dir = filepath.parents[2]
logs_dir = Taro_dir / "logs"
daily_routine_logs_path = logs_dir / "daily_routine_logs"
