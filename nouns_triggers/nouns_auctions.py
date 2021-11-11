import logging
from typing import TypedDict, Optional, Any

from django.conf import settings
from django.urls import reverse

from nouns_triggers.subgraph import query_subgraph
from nouns_triggers.utils import get_web3, to_iso_format, wei_to_eth

logger = logging.getLogger(__name__)


NOUNS_DAO_EXECUTOR_ADDRESS = '0x0BC3807Ec262cB779b38D65b38158acC3bfedE10'


class BaseAuction(TypedDict):
    id: int
    start_time_timestamp: int
    start_time_iso_format: str
    end_time_timestamp: int
    end_time_iso_format: str
    noun_img: str
    bid_wei: int
    bid_eth: float


class CurrentAuction(BaseAuction):
    treasury_balance_wei: int
    treasury_balance_eth: float
    bidder: str
    previous_auction: Optional[Any]


class PreviousAuction(BaseAuction):
    winner: str


def get_current_auction() -> CurrentAuction:
    """
    Get data about the current active Noun auction and the previous auction (that already ended).
    Data is fetched from the nouns subgraph on thegraph.com
    """
    subgraph_response = query_subgraph("""
                    query {
                        auctions(orderBy: startTime, orderDirection: desc, first: 2) {
                            id
                            startTime
                            endTime
                            amount
                            bidder { id }
                        }
                    }
                    """)
    current_auction, previous_auction = subgraph_response['auctions'][0], subgraph_response['auctions'][1]
    auction = build_current_auction_object(current_auction)
    auction['previous_auction'] = create_previous_auction_obj(previous_auction)

    return auction


def build_current_auction_object(auction_data_from_graph: dict) -> CurrentAuction:
    treasury_balance_wei = get_treasury_balance_wei()
    auction = CurrentAuction(
        bidder=auction_data_from_graph.get('bidder', {}).get('id'),
        treasury_balance_eth=wei_to_eth(treasury_balance_wei),
        treasury_balance_wei=treasury_balance_wei,
        **build_base_auction_obj(auction_data_from_graph)
    )
    return auction


def create_previous_auction_obj(previous_auction: dict) -> PreviousAuction:
    return PreviousAuction(
        winner=previous_auction['bidder']['id'],
        **build_base_auction_obj(previous_auction)
    )


def build_base_auction_obj(auction_data_from_graph: dict) -> BaseAuction:
    bid_wei = int(auction_data_from_graph['amount'])
    start_time_timestamp = int(auction_data_from_graph['startTime'])
    end_time_timestamp = int(auction_data_from_graph['endTime'])
    noun_id = int(auction_data_from_graph['id'])
    auction = BaseAuction(
        id=noun_id,
        bid_wei=bid_wei,
        bid_eth=wei_to_eth(bid_wei),
        start_time_timestamp=start_time_timestamp,
        end_time_timestamp=end_time_timestamp,
        start_time_iso_format=to_iso_format(start_time_timestamp),
        end_time_iso_format=to_iso_format(end_time_timestamp),
        noun_img=get_url_for_noun_img(noun_id),
    )
    return auction


def get_treasury_balance_wei() -> int:
    return get_web3().eth.get_balance(NOUNS_DAO_EXECUTOR_ADDRESS)


def get_url_for_noun_img(noun_id):
    return settings.BASE_URL + reverse('noun-img', args=[noun_id])