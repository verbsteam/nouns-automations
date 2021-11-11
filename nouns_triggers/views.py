import logging

from cairosvg import svg2png
from django.http import JsonResponse, HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework.response import Response
from rest_framework.views import APIView

from nouns_triggers import nouns_auctions, tasks, nouns_img, nouns_proposals
from nouns_triggers.models import RegisteredWebhook, AUCTION_SETTLED_EVENT

logger = logging.getLogger(__name__)


def get_auctions(request):
    auctions = [nouns_auctions.get_current_auction()]
    return JsonResponse(auctions, safe=False)


def get_png_for_noun_id(request, noun_id: int):
    noun_svg = nouns_img.get_noun_svg(noun_id)
    noun_png = svg2png(bytestring=noun_svg)
    return HttpResponse(noun_png, content_type="image/png")


def get_proposals(request):
    logger.info("Got request for proposals")
    proposals = nouns_proposals.get_proposals()
    logger.info(f"Returning {len(proposals)} proposals")
    return JsonResponse(proposals, safe=False)


def get_proposals_time_updates(request):
    proposal_time_updates = nouns_proposals.get_proposal_time_updates()
    return JsonResponse(proposal_time_updates, safe=False)


class WebhookRegistrationView(APIView):
    def post(self, request):
        webhook_url = request.data['webhook_url']
        hours = request.data['hours']
        minutes = request.data['minutes']

        logger.info(f"Got webhook registration request {webhook_url=} {hours=} {minutes=}")
        registered_webhook = RegisteredWebhook.objects.create(
            webhook_url=webhook_url,
            hours_before=hours,
            minutes_before=minutes,
            event=AUCTION_SETTLED_EVENT
        )

        tasks.schedule_trigger_for_new_registered_webhook(registered_webhook)

        return Response({'id': registered_webhook.uuid})

    def delete(self, request):
        webhook_id = request.data['webhook_id']

        logger.info(f"Got webhook delete request {webhook_id=}")

        registered_webhook = get_object_or_404(RegisteredWebhook, uuid=webhook_id)
        registered_webhook.delete()

        return Response()


def before_auction_example(request):
    current_auction = nouns_auctions.get_current_auction()
    return JsonResponse([current_auction], safe=False)


class ZapierAuthView(APIView):
    def post(self, request):
        resp_body = {
            'label': 'anonymous'
        }

        return Response(resp_body)
