import base64
import json
import os

from nouns_triggers.utils import get_web3

NOUNS_TOKEN_ADDRESS = "0x9C8fF314C9Bc7F6e59A9d9225Fb22946427eDC03"


def get_noun_svg(noun_id: int) -> bytes:
    w3 = get_web3()
    abi = get_nouns_token_abi()
    contract_instance = w3.eth.contract(address=NOUNS_TOKEN_ADDRESS, abi=abi)
    data = contract_instance.functions.dataURI(noun_id).call()
    j = json.loads(base64.b64decode(data.split(',')[1]))
    svg_data_uri = j['image']
    svg = base64.b64decode(svg_data_uri.split(',')[1])
    return svg


def get_nouns_token_abi():
    abi_path = os.path.join(os.path.dirname(__file__), 'abi/NounsToken.json')
    with open(abi_path) as f:
        return f.read()
