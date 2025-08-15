import argparse

from taro.cli.taro_daily_cli import TaroDailyCli
from taro.cli.taro_web_cli import TaroWebCli
from taro.cli.taro_web_prod_flask_cli import TaroWebProdFlaskCli
from taro.cli.taro_web_prod_bokeh_cli import TaroWebProdBokehCli
from taro.cli.taro_daemon_cli import TaroDaemonCli
from taro.cli.taro_drop_cli import TaroDropCli
from taro.cli.taro_backfill_cli import TaroBackfillCli
from taro.cli.taro_query_cli import TaroQueryCli

def main():
    clis = [TaroDailyCli(), TaroWebCli(), TaroWebProdFlaskCli(), TaroWebProdBokehCli(), TaroDaemonCli(), TaroDropCli(), TaroBackfillCli(), TaroQueryCli()]
    parser = argparse.ArgumentParser(
                    prog='Taro',
                    description='Taro is a program',
                    epilog='Text at the bottom of help')
    subparsers = parser.add_subparsers(dest='sub_cmd')
    subparsers.required = True
    for cli in clis:
        parser_cli = subparsers.add_parser(cli.get_name())
        cli.populate_subparser(parser_cli)
    args = parser.parse_args()
    for cli in clis:
        if args.sub_cmd == cli.get_name():
            cli.run(args)

if __name__ == "__main__":
    main()
