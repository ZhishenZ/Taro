import sys
import getpass
from pathlib import Path
from paths import Taro_dir, venv_dir, daily_service_logs_dir, service_templates_dir, service_files_dir
from mako.template import Template


def generate_service(service_name: str):
    """
    Generate a systemd service file from a mako template.

    Args:
        service_name (str): The base name for the service (e.g., "taro_daily").
    """
    username = getpass.getuser()
    venv_python = venv_dir / "bin" / "python"

    # Load template
    template = Template(filename=str(service_templates_dir / "taro_daily.service.mako"))

    # Render service file
    service_content = template.render(
        username=username,
        project_dir=Taro_dir,
        venv_python=venv_python,
        log_dir=daily_service_logs_dir,
    )

    # Ensure the 'service' folder exists
    service_files_dir.mkdir(parents=True, exist_ok=True)

    # Save service file inside 'service' folder
    service_file = service_files_dir / f"{service_name}.service"
    service_file.write_text(service_content)

    print(f"✅ Generated {service_file}")


if __name__ == "__main__":
    # Example usage
    generate_service(sys.argv[1])
