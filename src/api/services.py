"""Database Services."""
# Standard Python Libraries
import logging

# Third-Party Libraries
import pymongo
from rest_framework import serializers

# cisagov Libraries
from api.models import (
    campaign_models,
    customer_models,
    dhs_models,
    landing_page_models,
    recommendations_models,
    subscription_models,
    tag_models,
    target_history_models,
    template_models,
)
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
from api.utils import db_utils as db


class DBService:
    """Base Class for a Service."""

    def __init__(
        self,
        collection,
        model,
        save_serializer,
        update_serializer,
    ):
        """Init Base Class."""
        self.collection = collection
        self.model = model
        self.save_serializer = save_serializer
        self.update_serializer = update_serializer

    def validate_serializer(self, serializer):
        """Validate Serializer."""
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            logging.exception(e)
            raise e

    def convert_fields(self, fields):
        """Convert Fields."""
        if not fields:
            return None
        result = {}
        for field in fields:
            result[field] = 1
        return result

    def delete(self, uuid):
        """Delete."""
        return db.delete_single(
            uuid=str(uuid),
            collection=self.collection,
            model=self.model,
        )

    def get(self, uuid, fields=None):
        """Get."""
        fields = self.convert_fields(fields)
        return db.get(
            uuid=str(uuid),
            collection=self.collection,
            model=self.model,
            fields=fields,
        )

    def get_single(self, parameters, fields=None):
        """Get Single."""
        fields = self.convert_fields(fields)
        return db.get_single(
            parameters=parameters,
            collection=self.collection,
            model=self.model,
            fields=fields,
        )

    def get_list(self, parameters=None, fields=None):
        """Get List."""
        fields = self.convert_fields(fields)
        return db.get_list(
            parameters=parameters,
            collection=self.collection,
            model=self.model,
            fields=fields,
        )

    def save(self, data):
        """Save."""
        serializer = self.save_serializer(data=data)
        self.validate_serializer(serializer)
        result = db.save_single(
            post_data=serializer.validated_data,
            collection=self.collection,
            model=self.model,
        )
        if type(result) is dict:
            if result.get("errors"):
                logging.error(result.get("errors"))
                raise Exception(result.get("errors"))

        return result

    def update(self, uuid, data):
        """Update."""
        serializer = self.update_serializer(data=data)
        self.validate_serializer(serializer)
        result = db.update_single(
            uuid=str(uuid),
            put_data=serializer.validated_data,
            collection=self.collection,
            model=self.model,
        )
        if type(result) is dict:
            if result.get("errors"):
                logging.error(result.get("errors"))
                raise Exception(result.get("errors"))
        return result

    def update_nested(self, uuid, field, data, params=None):
        """Update Nested."""
        return db.update_nested_single(
            uuid=str(uuid),
            field=field,
            put_data=data,
            collection=self.collection,
            model=self.model,
            params=params,
        )

    def push_nested(self, uuid, field, data, params=None):
        """Push Nested."""
        return db.push_nested_item(
            uuid=str(uuid),
            field=field,
            put_data=data,
            collection=self.collection,
            model=self.model,
            params=params,
        )

    def exists(self, parameters=None):
        """Check exists."""
        return db.exists(
            parameters=parameters,
            collection=self.collection,
            model=self.model,
        )


class CampaignService(DBService):
    """CampaignService."""

    def __init__(self):
        """Init CampaignService."""
        return super().__init__(
            collection="campaign",
            model=campaign_models.GoPhishCampaignsModel,
            save_serializer=campaign_serializers.GoPhishCampaignsPostSerializer,
            update_serializer=campaign_serializers.GoPhishCampaignsPatchSerializer,
        )


class LandingPageService(DBService):
    """LandingPageService."""

    def __init__(self):
        """Init LandingPageService."""
        return super().__init__(
            collection="landing_page",
            model=landing_page_models.LandingPageModel,
            save_serializer=landing_page_serializers.LandingPagePostSerializer,
            update_serializer=landing_page_serializers.LandingPagePatchSerializer,
        )

    def clear_and_set_default(self, uuid):
        """Set Deaujlt Landing Page."""
        db_url = db.get_mongo_uri()
        client = pymongo.MongoClient(db_url)
        collection = client["pca_data_dev"]["landing_page"]
        sub_query = {}
        newvalues = {"$set": {"is_default_template": False}}
        collection.update_many(sub_query, newvalues)
        sub_query = {"landing_page_uuid": str(uuid)}
        newvalues = {"$set": {"is_default_template": True}}
        collection.update_one(sub_query, newvalues)


class SubscriptionService(DBService):
    """SubscriptionService."""

    def __init__(self):
        """Init SubscriptionService."""
        self.campaign_service = CampaignService()
        return super().__init__(
            collection="subscription",
            model=subscription_models.SubscriptionModel,
            save_serializer=subscriptions_serializers.SubscriptionPostSerializer,
            update_serializer=subscriptions_serializers.SubscriptionPatchSerializer,
        )

    def get(self, uuid, fields=None):
        """Get Subscription."""
        fields = self.convert_fields(fields)
        subscription = db.get(
            uuid=str(uuid), collection=self.collection, model=self.model, fields=fields
        )

        if not fields or "campaigns" in fields:
            logging.info("Getting campaigns")
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
            model=recommendations_models.RecommendationsModel,
            save_serializer=recommendations_serializers.RecommendationsPostSerializer,
            update_serializer=recommendations_serializers.RecommendationsPatchSerializer,
        )


class TemplateService(DBService):
    """TemplateService."""

    def __init__(self):
        """Init TemplateService."""
        return super().__init__(
            collection="template",
            model=template_models.TemplateModel,
            save_serializer=template_serializers.TemplatePostSerializer,
            update_serializer=template_serializers.TemplatePatchSerializer,
        )


class TagService(DBService):
    """TagService."""

    def __init__(self):
        """Init TagService."""
        return super().__init__(
            collection="tag_definition",
            model=tag_models.TagModel,
            save_serializer=tag_serializers.TagPostSerializer,
            update_serializer=tag_serializers.TagPatchSerializer,
        )


class DHSContactService(DBService):
    """DHSContactService."""

    def __init__(self):
        """Init DHSContactService."""
        return super().__init__(
            collection="dhs_contact",
            model=dhs_models.DHSContactModel,
            save_serializer=dhs_serializers.DHSContactPostSerializer,
            update_serializer=dhs_serializers.DHSContactPatchSerializer,
        )


class CustomerService(DBService):
    """CustomerService."""

    def __init__(self):
        """Init CustomerService."""
        return super().__init__(
            collection="customer",
            model=customer_models.CustomerModel,
            save_serializer=customer_serializers.CustomerPostSerializer,
            update_serializer=customer_serializers.CustomerPatchSerializer,
        )


class TargetHistoryService(DBService):
    """TargetHistoryService."""

    def __init__(self):
        """Init TargetHistoryService."""
        return super().__init__(
            collection="target",
            model=target_history_models.TargetHistoryModel,
            save_serializer=target_history_serializers.TargetHistoryPostSerializer,
            update_serializer=target_history_serializers.TargetHistoryPatchSerializer,
        )
