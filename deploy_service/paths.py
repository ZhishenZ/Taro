from pathlib import Path

filepath = Path(__file__)
Taro_dir = filepath.parents[1]
venv_dir = Taro_dir.parent / "taro_venv"
service_templates_dir = filepath.parent / "service_templates"
logs_dir = Taro_dir / "logs"
daily_service_logs_dir = logs_dir / "daily_service_logs"
daily_service_logs_dir.mkdir(parents=True, exist_ok=True)

deploy_service_output_dir = filepath.parent / "output"
deploy_service_output_dir.mkdir(parents=True, exist_ok=True)
service_files_dir = deploy_service_output_dir / "service"
paths_sh_path = deploy_service_output_dir / "paths.sh"
with open(paths_sh_path, "w+") as f:
    f.write(f"TARO_DIR={Taro_dir}\n")
    f.write(f"VENV_DIR={venv_dir}\n")
    f.write(f"service_templates_dir={service_templates_dir}\n")
    f.write(f"logs_dir={logs_dir}\n")
    f.write(f"daily_service_logs_dir={daily_service_logs_dir}\n")
    f.write(f"SERVICE_FILE_DIR={service_files_dir}\n")
