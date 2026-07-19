"""Assembly of a single typed context package."""

from typing import Optional

from app.agents.context_models import (
    ContextPackage,
    CustomerAccount,
    CustomerOrder,
    CustomerProfile,
    PreviousResolution,
    TicketMetadata,
)


class ContextBuilder:
    """Builds immutable context packages from independently retrieved records."""

    async def build(
        self,
        *,
        ticket: TicketMetadata,
        customer: CustomerProfile,
        account: Optional[CustomerAccount],
        orders: tuple[CustomerOrder, ...],
        previous_tickets: tuple[TicketMetadata, ...],
        previous_resolutions: tuple[PreviousResolution, ...],
    ) -> ContextPackage:
        """Assemble the context contract consumed by future planning stages."""
        return ContextPackage(
            ticket=ticket,
            customer=customer,
            account=account,
            orders=orders,
            previous_tickets=previous_tickets,
            previous_resolutions=previous_resolutions,
            priority=ticket.priority,
            sentiment=ticket.sentiment,
            intent=ticket.intent,
        )
