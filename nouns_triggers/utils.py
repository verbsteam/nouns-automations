from datetime import datetime, timezone

from django.conf import settings
from ens import ENS
from web3 import Web3


ETH_IN_WEI = 10**18


def to_iso_format(unix_timestamp: int) -> str:
    """
    Parameters
    ----------
    unix_timestamp : unix timestamp

    Returns
    -------
    string with the date time in iso format, e.g: "2021-11-10T15:16:06+00:00"
    """
    return datetime.fromtimestamp(unix_timestamp, tz=timezone.utc).isoformat()


def get_web3():
    return Web3(Web3.HTTPProvider(f'https://eth-mainnet.alchemyapi.io/v2/{settings.ALCHEMY_API_KEY}'))


def get_ens():
    return ENS.fromWeb3(get_web3())


def get_ens_name(address: str) -> str:
    return get_ens().name(address)


def wei_to_eth(wei: int) -> float:
    return wei / ETH_IN_WEI
