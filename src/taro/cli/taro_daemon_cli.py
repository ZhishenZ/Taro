import argparse
import time
import sys
import subprocess
from datetime import datetime, timezone

from taro.cli.sub_cli import SubCli
from taro.paths import daily_routine_logs_path
from taro.configs import close_utc_hour
from taro.configs import tickers, daily_task_utc_hour

class RCO:
    def __init__(self, cmd, returncode, stdout, stderr):
        self.cmd = cmd
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr

    def __str__(self):
        retval = "### return code ###\n"
        retval += f"{self.returncode}\n"
        retval += f"### stdout ###\n"
        retval += f"{self.stdout}\n"
        retval += f"### stderr ###\n"
        retval += f"{self.stderr}\n"
        return retval

class TaroDaemonCli(SubCli):
    def get_name(self):
        return "daemon"

    def populate_subparser(self, subparser:argparse.ArgumentParser):
        subparser.add_argument("-t", "--test", action="store_true")
        subparser.add_argument("-c", "--cmd_output", action="store_true")
        subparser.add_argument("-s", "--sleep_time", default="10")

    def call_routine_task(self, ag):
        utc_dt = datetime.now(timezone.utc)
        if utc_dt.hour + (utc_dt.minute/60) < close_utc_hour + 0.1: # market not closed yet
            date = utc_dt.date() - datetime.timedelta(days=1)
        else:
            date = utc_dt.date()
        date = date.strftime("%Y-%m-%d")

        (daily_routine_logs_path/date).mkdir(parents=True, exist_ok=True)
        for ticker in tickers:
            cmd = ["taro", "daily"]
            if ag.cmd_output:
                result = subprocess.run(cmd)
            else:
                result = subprocess.run(
                    cmd,
                    stdout=subprocess.PIPE,   # Capture standard output
                    stderr=subprocess.PIPE,   # Capture standard error
                    text=True                 # Return output as strings (not bytes)
                )
                rco = RCO(cmd, result.returncode, result.stdout, result.stderr)
                with open(daily_routine_logs_path/date/f"{ticker}.log", "w+") as f:
                    f.write(rco.__str__())

    def run(self, ag):
        if ag.test:
            self.call_routine_task(ag)
        else:
            prev_hour = daily_task_utc_hour - 1
            while(1):
                time.sleep(float(ag.sleep_time))
                utc_dt = datetime.now(timezone.utc)
                curr_hour = utc_dt.hour
                if prev_hour == 19 and curr_hour == daily_task_utc_hour:
                    print(f"taro daily daemon call daily routine utc {utc_dt}")
                    sys.stdout.flush()
                    self.call_routine_task(ag)
                prev_hour = curr_hour
                sys.stdout.flush()

