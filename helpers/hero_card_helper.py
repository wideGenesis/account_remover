from botbuilder.core import CardFactory
from botbuilder.schema import ActionTypes, Attachment, HeroCard, CardAction

from lib.messages import WARNINGS


def create_hero_card() -> Attachment:
    card = HeroCard(
        title=f"{WARNINGS['online']}",
        buttons=[
            CardAction(
                type=ActionTypes.im_back,
                title=f"{WARNINGS['yes']}",
                value=f"{WARNINGS['yes']}",
            ),
        ],
    )
    return CardFactory.hero_card(card)
