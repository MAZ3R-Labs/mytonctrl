import json
import requests

from mypylib.mypylib import color_print


def check_config_url(url):
    try:
        r = requests.get(url, timeout=3)
        if r.status_code != 200:
            print(f'Failed to get config from {url}: {r.status_code} code; {r.text}')
            return
        return r.json()
    except Exception as e:
        print(f'Failed to get config from {url}: {e}')
        return


def check_config_file(path):
    try:
        with open(path, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f'Failed to read config from {path}: {e}')
        return


def get_config(path):
    if 'http' in path:
        config = check_config_url(path)
    else:
        config = check_config_file(path)
    if config is None:
        raise Exception(f'Failed to get config')
    return config


def add_collator_config_to_vc(local, ton, config: dict):
    local.add_log(f"Adding collator options config to validator console", "debug")
    path = ton.tempDir + f'/collator_config.json'
    with open(path, 'w') as f:
        json.dump(config, f)
    result = ton.validatorConsole.Run(f"setcollatoroptionsjson {path}")
    return 'success' in result, result


def set_collator_config(args):
    from mytonctrl import local, ton
    if len(args) != 1:
        color_print("{red}Bad args. Usage:{endc} set_collator_config <path/url>")
        return
    path = args[1]
    config = get_config(path)
    local.db['collator_config'] = config
    local.save()
    added, msg = add_collator_config_to_vc(local, ton, config)
    if not added:
        print(f'Failed to add collator config to validator console: {msg}')
        color_print("set_collator_config - {red}ERROR{endc}")
        return
    color_print("set_collator_config - {green}OK{endc}")


def update_collator_config(args):
    from mytonctrl import local, ton
    default = 'https://raw.githubusercontent.com/ton-blockchain/ton-blockchain.github.io/main/default_collator_options.json'
    location = local.db.get('collator_config', default)
    config = get_config(location)
    added, msg = add_collator_config_to_vc(local, ton, config)
    if not added:
        print(f'Failed to add collator config to validator console: {msg}')
        color_print("update_collator_config - {red}ERROR{endc}")
        return
    color_print("update_collator_config - {green}OK{endc}")
