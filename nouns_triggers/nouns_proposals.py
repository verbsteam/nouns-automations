import logging
import re
from datetime import datetime, timezone, timedelta
from typing import TypedDict, Union, Optional, List

from nouns_triggers.subgraph import query_subgraph
from nouns_triggers.utils import get_web3, wei_to_eth

logger = logging.getLogger(__name__)

AVG_ETH_BLOCK_TIME_IN_SECS = 13.3


class Proposal(TypedDict):
    id: Union[int, str]
    proposal_id: Optional[int]
    proposal_title: str
    proposal_description: str
    voting_start_block: int
    voting_end_block: int
    total_value_wei: int
    total_value_eth: float
    estimated_voting_start_time_timestamp: int
    estimated_voting_end_time_timestamp: int
    estimated_voting_start_time_iso_format: str
    estimated_voting_end_time_iso_format: str
    url: str


def get_proposals() -> List[Proposal]:
    """
    Returns the latest 3 proposals based on data from nouns subgraph
    """
    logger.info("Getting proposals from subgraph")
    subgraph_response = query_subgraph("""
                    query {
                        proposals(orderBy: startBlock, orderDirection: desc, first: 3) {
                            id
                            description
                            startBlock
                            endBlock
                            values
                        }
                    }
                    """)
    logger.info(f"Got {len(subgraph_response['proposals'])} proposals for subgraph")
    return [create_proposal_obj(p) for p in subgraph_response['proposals']]


def get_proposal_time_updates() -> List[Proposal]:
    """
    Since proposal voting times are based on blocks, we can only estimate the actual time at which they will happen.
    This function is used to get updates on these time estimates.
    The id field of each new proposal object is <proposal_id>_<current_block>, representing the time estimates
    calculated at <current_block> point in time.
    Since integromat & zapier are based on ids to identify new objects, this will make sure new objects are being
     pushed out.
    Returns
    -------
    List of active Proposal objects with the up to date estimated times.
    """
    subgraph_response = query_subgraph("""
                        query {
                            proposals(orderBy: startBlock, orderDirection: desc) {
                                id
                                description
                                startBlock
                                endBlock
                                values
                            }
                        }
                        """)

    current_block = get_web3().eth.block_number
    subgraph_proposals_voting_not_ended = [
        p for p in subgraph_response['proposals'] if int(p['endBlock']) > current_block]

    proposals: List[Proposal] = [create_proposal_obj(p) for p in subgraph_proposals_voting_not_ended]

    for proposal in proposals:
        proposal['id'] = f"{proposal['proposal_id']}_{current_block}"

    return proposals


def create_proposal_obj(proposal_dict_from_subgraph: dict) -> Proposal:
    total_value_wei = sum(map(int, proposal_dict_from_subgraph['values']))
    voting_start_block = int(proposal_dict_from_subgraph['startBlock'])
    voting_end_block = int(proposal_dict_from_subgraph['endBlock'])
    estimated_voting_start_dt = get_estimated_datetime_for_block_number(voting_start_block)
    estimated_voting_end_dt = get_estimated_datetime_for_block_number(voting_end_block)
    proposal_id = int(proposal_dict_from_subgraph['id'])
    return Proposal(
        id=proposal_id,
        proposal_id=proposal_id,
        proposal_title=extract_proposal_title(proposal_dict_from_subgraph),
        proposal_description=proposal_dict_from_subgraph['description'],
        voting_start_block=voting_start_block,
        voting_end_block=voting_end_block,
        total_value_wei=total_value_wei,
        total_value_eth=wei_to_eth(total_value_wei),
        estimated_voting_start_time_timestamp=int(estimated_voting_start_dt.timestamp()),
        estimated_voting_start_time_iso_format=estimated_voting_start_dt.isoformat(),
        estimated_voting_end_time_timestamp=int(estimated_voting_end_dt.timestamp()),
        estimated_voting_end_time_iso_format=estimated_voting_end_dt.isoformat(),
        url=f"https://nouns.wtf/vote/{proposal_id}"
    )


def get_estimated_datetime_for_block_number(block_number) -> datetime:
    w3 = get_web3()
    current_block = w3.eth.block_number
    if block_number <= current_block:
        return datetime.fromtimestamp(w3.eth.get_block(block_number)['timestamp'], tz=timezone.utc)
    else:
        blocks_away = block_number - current_block
        return datetime.now(tz=timezone.utc) + timedelta(
            seconds=blocks_away * AVG_ETH_BLOCK_TIME_IN_SECS)


def extract_proposal_title(proposal):
    return re.sub(r'^#\s*', '', proposal['description'].split('\n')[0])
