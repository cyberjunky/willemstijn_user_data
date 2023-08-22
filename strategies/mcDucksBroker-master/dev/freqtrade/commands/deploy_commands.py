import logging
import sys
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

import requests

from freqtrade.configuration import setup_utils_configuration
from freqtrade.configuration.directory_operations import copy_sample_files, create_userdata_dir
from freqtrade.constants import USERPATH_HYPEROPTS, USERPATH_STRATEGIES
from freqtrade.exceptions import OperationalException
from freqtrade.misc import render_template, render_template_with_fallback
from freqtrade.state import RunMode


logger = logging.getLogger(__name__)


def start_create_userdir(args: Dict[str, Any]) -> None:
    """
    Create "user_data" directory to contain user data strategies, hyperopt, ...)
    :param args: Cli args from Arguments()
    :return: None
    """
    if "user_data_dir" in args and args["user_data_dir"]:
        userdir = create_userdata_dir(args["user_data_dir"], create_dir=True)
        copy_sample_files(userdir, overwrite=args["reset"])
    else:
        logger.warning("`create-userdir` requires --userdir to be set.")
        sys.exit(1)


def deploy_new_strategy(strategy_name: str, strategy_path: Path, subtemplate: str) -> None:
    """
    Deploy new strategy from template to strategy_path
    """
    fallback = 'full'
    indicators = render_template_with_fallback(
        templatefile=f"subtemplates/indicators_{subtemplate}.j2",
        templatefallbackfile=f"subtemplates/indicators_{fallback}.j2",
        )
    buy_trend = render_template_with_fallback(
        templatefile=f"subtemplates/buy_trend_{subtemplate}.j2",
        templatefallbackfile=f"subtemplates/buy_trend_{fallback}.j2",
        )
    sell_trend = render_template_with_fallback(
        templatefile=f"subtemplates/sell_trend_{subtemplate}.j2",
        templatefallbackfile=f"subtemplates/sell_trend_{fallback}.j2",
        )
    plot_config = render_template_with_fallback(
        templatefile=f"subtemplates/plot_config_{subtemplate}.j2",
        templatefallbackfile=f"subtemplates/plot_config_{fallback}.j2",
    )
    additional_methods = render_template_with_fallback(
        templatefile=f"subtemplates/strategy_methods_{subtemplate}.j2",
        templatefallbackfile="subtemplates/strategy_methods_empty.j2",
    )

    strategy_text = render_template(templatefile='base_strategy.py.j2',
                                    arguments={"strategy": strategy_name,
                                               "indicators": indicators,
                                               "buy_trend": buy_trend,
                                               "sell_trend": sell_trend,
                                               "plot_config": plot_config,
                                               "additional_methods": additional_methods,
                                               })

    logger.info(f"Writing strategy to `{strategy_path}`.")
    strategy_path.write_text(strategy_text)


def start_new_strategy(args: Dict[str, Any]) -> None:

    config = setup_utils_configuration(args, RunMode.UTIL_NO_EXCHANGE)

    if "strategy" in args and args["strategy"]:
        if args["strategy"] == "DefaultStrategy":
            raise OperationalException("DefaultStrategy is not allowed as name.")

        new_path = config['user_data_dir'] / USERPATH_STRATEGIES / (args['strategy'] + '.py')

        if new_path.exists():
            raise OperationalException(f"`{new_path}` already exists. "
                                       "Please choose another Strategy Name.")

        deploy_new_strategy(args['strategy'], new_path, args['template'])

    else:
        raise OperationalException("`new-strategy` requires --strategy to be set.")


def deploy_new_hyperopt(hyperopt_name: str, hyperopt_path: Path, subtemplate: str) -> None:
    """
    Deploys a new hyperopt template to hyperopt_path
    """
    fallback = 'full'
    buy_guards = render_template_with_fallback(
        templatefile=f"subtemplates/hyperopt_buy_guards_{subtemplate}.j2",
        templatefallbackfile=f"subtemplates/hyperopt_buy_guards_{fallback}.j2",
        )
    sell_guards = render_template_with_fallback(
        templatefile=f"subtemplates/hyperopt_sell_guards_{subtemplate}.j2",
        templatefallbackfile=f"subtemplates/hyperopt_sell_guards_{fallback}.j2",
        )
    buy_space = render_template_with_fallback(
        templatefile=f"subtemplates/hyperopt_buy_space_{subtemplate}.j2",
        templatefallbackfile=f"subtemplates/hyperopt_buy_space_{fallback}.j2",
        )
    sell_space = render_template_with_fallback(
        templatefile=f"subtemplates/hyperopt_sell_space_{subtemplate}.j2",
        templatefallbackfile=f"subtemplates/hyperopt_sell_space_{fallback}.j2",
        )

    strategy_text = render_template(templatefile='base_hyperopt.py.j2',
                                    arguments={"hyperopt": hyperopt_name,
                                               "buy_guards": buy_guards,
                                               "sell_guards": sell_guards,
                                               "buy_space": buy_space,
                                               "sell_space": sell_space,
                                               })

    logger.info(f"Writing hyperopt to `{hyperopt_path}`.")
    hyperopt_path.write_text(strategy_text)


def start_new_hyperopt(args: Dict[str, Any]) -> None:

    config = setup_utils_configuration(args, RunMode.UTIL_NO_EXCHANGE)

    if 'hyperopt' in args and args['hyperopt']:
        if args['hyperopt'] == 'DefaultHyperopt':
            raise OperationalException("DefaultHyperopt is not allowed as name.")

        new_path = config['user_data_dir'] / USERPATH_HYPEROPTS / (args['hyperopt'] + '.py')

        if new_path.exists():
            raise OperationalException(f"`{new_path}` already exists. "
                                       "Please choose another Hyperopt Name.")
        deploy_new_hyperopt(args['hyperopt'], new_path, args['template'])
    else:
        raise OperationalException("`new-hyperopt` requires --hyperopt to be set.")


def clean_ui_subdir(directory: Path):
    if directory.is_dir():
        logger.info("Removing UI directory content.")

        for p in reversed(list(directory.glob('**/*'))):  # iterate contents from leaves to root
            if p.name in ('.gitkeep', 'fallback_file.html'):
                continue
            if p.is_file():
                p.unlink()
            elif p.is_dir():
                p.rmdir()


def read_ui_version(dest_folder: Path) -> Optional[str]:
    file = dest_folder / '.uiversion'
    if not file.is_file():
        return None

    with file.open('r') as f:
        return f.read()


def download_and_install_ui(dest_folder: Path, dl_url: str, version: str):
    from io import BytesIO
    from zipfile import ZipFile

    logger.info(f"Downloading {dl_url}")
    resp = requests.get(dl_url).content
    dest_folder.mkdir(parents=True, exist_ok=True)
    with ZipFile(BytesIO(resp)) as zf:
        for fn in zf.filelist:
            with zf.open(fn) as x:
                destfile = dest_folder / fn.filename
                if fn.is_dir():
                    destfile.mkdir(exist_ok=True)
                else:
                    destfile.write_bytes(x.read())
    with (dest_folder / '.uiversion').open('w') as f:
        f.write(version)


def get_ui_download_url() -> Tuple[str, str]:
    base_url = 'https://api.github.com/repos/freqtrade/frequi/'
    # Get base UI Repo path

    resp = requests.get(f"{base_url}releases")
    resp.raise_for_status()
    r = resp.json()

    latest_version = r[0]['name']
    assets = r[0].get('assets', [])
    dl_url = ''
    if assets and len(assets) > 0:
        dl_url = assets[0]['browser_download_url']

    # URL not found - try assets url
    if not dl_url:
        assets = r[0]['assets_url']
        resp = requests.get(assets)
        r = resp.json()
        dl_url = r[0]['browser_download_url']

    return dl_url, latest_version


def start_install_ui(args: Dict[str, Any]) -> None:

    dest_folder = Path(__file__).parents[1] / 'rpc/api_server/ui/installed/'
    # First make sure the assets are removed.
    dl_url, latest_version = get_ui_download_url()

    curr_version = read_ui_version(dest_folder)
    if curr_version == latest_version and not args.get('erase_ui_only'):
        logger.info(f"UI already up-to-date, FreqUI Version {curr_version}.")
        return

    clean_ui_subdir(dest_folder)
    if args.get('erase_ui_only'):
        logger.info("Erased UI directory content. Not downloading new version.")
    else:
        # Download a new version
        download_and_install_ui(dest_folder, dl_url, latest_version)
