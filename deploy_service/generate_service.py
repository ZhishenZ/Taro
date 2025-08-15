import sys
import getpass
from pathlib import Path
from paths import Taro_dir, daily_service_logs_dir, service_templates_dir, service_files_dir
from mako.template import Template


def generate_service(service_name: str, venv_python_path: str = None):
    """
    Generate a systemd service file from a mako template.

    Args:
        service_name (str): The base name for the service (e.g., "taro_daily").
        venv_python_path (str): Path to the venv python executable. If not provided, uses current python.
    """
    username = getpass.getuser()

    # Use provided python path or default to current python
    if venv_python_path:
        venv_python = Path(venv_python_path)
    else:
        venv_python = Path(sys.executable)

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
    # Example usage: python generate_service.py <service_name> [venv_python_path]
    service_name = sys.argv[1]
    venv_python_path = sys.argv[2] if len(sys.argv) > 2 else None
    generate_service(service_name, venv_python_path)
