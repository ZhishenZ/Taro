[Unit]
Description=Taro Python Project
After=network.target

[Service]
Type=simple
User=${username}
WorkingDirectory=${project_dir}
ExecStart=${venv_python} -m taro.cli.__main__ daemon -s 0.1
Restart=always
RestartSec=20
StandardOutput=append:${log_dir}/taro.out.log
StandardError=append:${log_dir}/taro.err.log

[Install]
WantedBy=multi-user.target
