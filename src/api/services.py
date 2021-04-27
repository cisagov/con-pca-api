"""Database Services."""
# Standard Python Libraries
from datetime import datetime
import logging
from uuid import uuid4

# Third-Party Libraries
from rest_framework import serializers

# cisagov Libraries
from api.serializers import (
    campaign_serializers,
    customer_serializers,
    dhs_serializers,
    landing_page_serializers,
    recommendations_serializers,
    subscriptions_serializers,
    tag_serializers,
    target_history_serializers,
    template_serializers,
)
from config.settings import DB


class DBService:
    """Base Class for a Service."""

    def __init__(
        self,
        collection,
        save_serializer,
        update_serializer,
    ):
        """Init Base Class."""
        self.collection = collection
        self.save_serializer = save_serializer
        self.update_serializer = update_serializer
        self.uuid_field = f"{collection}_uuid"
        self.db = getattr(DB, collection)

    def validate_serializer(self, serializer):
        """Validate Serializer."""
        try:
            serializer.is_valid(raise_exception=True)
            return serializer.validated_data
        except serializers.ValidationError as e:
            logging.exception(e)
            raise e

    def convert_fields(self, fields):
        """Convert Fields."""
        if not fields:
            return {"_id": 0}
        result = {}
        for field in fields:
            result[field] = 1
        result["_id"] = 0
        return result

    def delete(self, uuid):
        """Delete."""
        self.db.delete_one({self.uuid_field: str(uuid)})
        return {self.uuid_field: str(uuid)}

    def get(self, uuid, fields=None):
        """Get."""
        fields = self.convert_fields(fields)
        return self.db.find_one(
            {self.uuid_field: str(uuid)}, self.convert_fields(fields)
        )

    def get_single(self, parameters, fields=None):
        """Get Single."""
        fields = self.convert_fields(fields)
        return self.db.find_one(parameters, fields)

    def get_list(self, parameters=None, fields=None):
        """Get List."""
        fields = self.convert_fields(fields)
        return list(self.db.find(parameters, fields))

    def save(self, data):
        """Save."""
        serializer = self.save_serializer(data=data)
        data = self.validate_serializer(serializer)

        # Add on uuid field
        data[self.uuid_field] = str(uuid4())

        # Add on db tracking fields
        data["created_by"] = data["last_updated_by"] = "dev user"
        data["cb_timestamp"] = data["lub_timestamp"] = datetime.utcnow()

        # Save data
        self.db.insert_one(data)
        return {self.uuid_field: data[self.uuid_field]}

    def update(self, uuid, data):
        """Update."""
        serializer = self.update_serializer(data=data)
        data = self.validate_serializer(serializer)

        # Update updated fields
        data["last_update_by"] = "dev user"
        data["lub_timestamp"] = datetime.utcnow()

        # Update Data
        self.db.update_one({self.uuid_field: str(uuid)}, {"$set": data})
        return {self.uuid_field: uuid}

    def update_nested(self, uuid, field, data, params=None):
        """Update Nested."""
        return self.db.update_one(
            {self.uuid_field: str(uuid), **params}, {"$set": {field: data}}
        ).raw_result

    def push_nested(self, uuid, field, data):
        """Push Nested."""
        return self.db.update_one(
            {self.uuid_field: str(uuid)}, {"$push": {field: data}}
        ).raw_result

    def exists(self, parameters=None):
        """Check exists."""
        fields = self.convert_fields([self.uuid_field])
        result = list(self.db.find(parameters, fields))
        if result:
            return True
        return False

    def random(self, count=1):
        """Select a random record from collection."""
        return list(self.db.aggregate([{"$sample": {"size": count}}]))


class CampaignService(DBService):
    """CampaignService."""

    def __init__(self):
        """Init CampaignService."""
        return super().__init__(
            collection="campaign",
            save_serializer=campaign_serializers.GoPhishCampaignsPostSerializer,
            update_serializer=campaign_serializers.GoPhishCampaignsPatchSerializer,
        )


class LandingPageService(DBService):
    """LandingPageService."""

    def __init__(self):
        """Init LandingPageService."""
        return super().__init__(
            collection="landing_page",
            save_serializer=landing_page_serializers.LandingPagePostSerializer,
            update_serializer=landing_page_serializers.LandingPagePatchSerializer,
        )

    def clear_and_set_default(self, uuid):
        """Set Default Landing Page."""
        sub_query = {}
        newvalues = {"$set": {"is_default_template": False}}
        self.db.update_many(sub_query, newvalues)
        sub_query = {"landing_page_uuid": str(uuid)}
        newvalues = {"$set": {"is_default_template": True}}
        self.db.update_one(sub_query, newvalues)


class SubscriptionService(DBService):
    """SubscriptionService."""

    def __init__(self):
        """Init SubscriptionService."""
        self.campaign_service = CampaignService()
        return super().__init__(
            collection="subscription",
            save_serializer=subscriptions_serializers.SubscriptionPostSerializer,
            update_serializer=subscriptions_serializers.SubscriptionPatchSerializer,
        )

    def get(self, uuid, fields=None):
        """Get Subscription."""
        subscription = self.db.find_one(
            {self.uuid_field: str(uuid)}, self.convert_fields(fields)
        )

        if subscription and (not fields or "campaigns" in fields):
            subscription["campaigns"] = self.campaign_service.get_list(
                {"subscription_uuid": str(uuid)}
            )
        return subscription


class RecommendationService(DBService):
    """RecommendationService."""

    def __init__(self):
        """Init RecommendationService."""
        return super().__init__(
            collection="recommendations",
            save_serializer=recommendations_serializers.RecommendationsPostSerializer,
            update_serializer=recommendations_serializers.RecommendationsPatchSerializer,
        )


class TemplateService(DBService):
    """TemplateService."""

    def __init__(self):
        """Init TemplateService."""
        return super().__init__(
            collection="template",
            save_serializer=template_serializers.TemplatePostSerializer,
            update_serializer=template_serializers.TemplatePatchSerializer,
        )


class TagService(DBService):
    """TagService."""

    def __init__(self):
        """Init TagService."""
        return super().__init__(
            collection="tag_definition",
            save_serializer=tag_serializers.TagPostSerializer,
            update_serializer=tag_serializers.TagPatchSerializer,
        )


class DHSContactService(DBService):
    """DHSContactService."""

    def __init__(self):
        """Init DHSContactService."""
        return super().__init__(
            collection="dhs_contact",
            save_serializer=dhs_serializers.DHSContactPostSerializer,
            update_serializer=dhs_serializers.DHSContactPatchSerializer,
        )


class CustomerService(DBService):
    """CustomerService."""

    def __init__(self):
        """Init CustomerService."""
        return super().__init__(
            collection="customer",
            save_serializer=customer_serializers.CustomerPostSerializer,
            update_serializer=customer_serializers.CustomerPatchSerializer,
        )


class TargetHistoryService(DBService):
    """TargetHistoryService."""

    def __init__(self):
        """Init TargetHistoryService."""
        return super().__init__(
            collection="target",
            save_serializer=target_history_serializers.TargetHistoryPostSerializer,
            update_serializer=target_history_serializers.TargetHistoryPatchSerializer,
        )
