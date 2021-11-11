import logging
from typing import Optional

import requests
from django_q.models import Schedule
from django_q.tasks import schedule

from nouns_triggers import nouns_auctions
from nouns_triggers.models import LastSeenAuction, RegisteredWebhook, AUCTION_SETTLED_EVENT
from nouns_triggers.nouns_auctions import CurrentAuction
from datetime import datetime, timezone, timedelta

logger = logging.getLogger(__name__)


def check_for_new_auction():
    """
    Repeatedly checks if there are new auctions. If there are, schedules task to invoke the registered webhooks
    X time before the auction is scheduled to end
    """
    try:
        logger.debug("Checking for new auctions")
        current_auction = nouns_auctions.get_current_auction()
        last_seen_auction = get_last_seen_auction_id()
        if current_auction['id'] > last_seen_auction:
            schedule_before_auction_settles_triggers(current_auction)
            set_last_seen_auction_id(current_auction['id'])
        logger.debug("Done")
    except Exception as e:
        logger.warning("Exception while checking for new auction", exc_info=True)


def get_last_seen_auction_id() -> int:
    last_seen_auction: Optional[LastSeenAuction] = LastSeenAuction.objects.first()
    if last_seen_auction is None:
        return 0
    else:
        return last_seen_auction.noun_id


def set_last_seen_auction_id(noun_id):
    last_seen_auction: Optional[LastSeenAuction] = LastSeenAuction.objects.first()
    if last_seen_auction is None:
        LastSeenAuction.objects.create(noun_id=noun_id)
    else:
        last_seen_auction.noun_id = noun_id
        last_seen_auction.save()


def schedule_before_auction_settles_triggers(current_auction: CurrentAuction):
    logger.info(f"Scheduling before-auction-settles triggers for action id: {current_auction['id']}")

    registered_webhook: RegisteredWebhook
    for registered_webhook in RegisteredWebhook.objects.filter(event=AUCTION_SETTLED_EVENT):
        schedule_webhook_trigger_before_current_auction_ends(current_auction, registered_webhook)


def schedule_webhook_trigger_before_current_auction_ends(
        current_auction: CurrentAuction, registered_webhook: RegisteredWebhook):
    auction_end_time = datetime.fromtimestamp(current_auction['end_time_timestamp'], tz=timezone.utc)
    trigger_time = auction_end_time - timedelta(
        hours=registered_webhook.hours_before, minutes=registered_webhook.minutes_before)

    logger.info(f"Scheduling trigger for registered_webhook id: {registered_webhook.id} at {trigger_time}")
    schedule(
        func='nouns_triggers.tasks.send_current_auction_to_webhook',
        next_run=trigger_time,
        schedule_type=Schedule.ONCE,
        **{'registered_webhook_id': registered_webhook.id},
    )


def schedule_trigger_for_new_registered_webhook(registered_webhook: RegisteredWebhook):
    current_auction = nouns_auctions.get_current_auction()
    schedule_webhook_trigger_before_current_auction_ends(current_auction, registered_webhook)


def send_current_auction_to_webhook(registered_webhook_id):
    logger.info(f"Sending current auction to {registered_webhook_id=}")
    registered_webhook: RegisteredWebhook = RegisteredWebhook.objects.filter(id=registered_webhook_id).first()

    if registered_webhook is None:
        logger.info(f"Didn't find obj with {registered_webhook_id=}, must've been deleted")
        return

    current_auction = nouns_auctions.get_current_auction()

    logger.debug(f"Sending current auction to webhook_url={registered_webhook.webhook_url}")
    requests.post(url=registered_webhook.webhook_url, json=current_auction)
