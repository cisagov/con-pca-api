import logging
from rest_framework import serializers
import pymongo

from api.utils import db_utils as db

from api.models import campaign_models
from api.serializers import campaign_serializers

from api.models import customer_models
from api.serializers import customer_serializers

from api.models import dhs_models
from api.serializers import dhs_serializers

from api.models import landing_page_models
from api.serializers import landing_page_serializers

from api.models import recommendations_models
from api.serializers import recommendations_serializers

from api.models import subscription_models
from api.serializers import subscriptions_serializers

from api.models import tag_models
from api.serializers import tag_serializers

from api.models import target_history_models
from api.serializers import target_history_serializers

from api.models import template_models
from api.serializers import template_serializers


class DBService:
    def __init__(
        self,
        collection,
        model,
        validation,
        model_serializer,
        response_serializer,
        save_serializer,
        update_serializer,
    ):
        self.collection = collection
        self.model = model
        self.validation = validation
        self.model_serializer = model_serializer
        self.response_serializer = response_serializer
        self.save_serializer = save_serializer
        self.update_serializer = update_serializer

    def validate_serializer(self, serializer):
        try:
            serializer.is_valid(raise_exception=True)
        except serializers.ValidationError as e:
            logging.exception(e)
            raise e

    def delete(self, uuid):
        resp = db.delete_single(
            uuid=uuid,
            collection=self.collection,
            model=self.model,
            validation_model=self.validation,
        )
        serializer = self.response_serializer(data=resp)
        self.validate_serializer(serializer)
        return serializer.data

    def get(self, uuid):
        result = db.get_single(
            uuid=uuid,
            collection=self.collection,
            model=self.model,
            validation_model=self.validation,
        )
        serializer = self.model_serializer(data=result)
        self.validate_serializer(serializer)

        return serializer.data

    def get_list(self, parameters=None, fields=None):
        result = db.get_list(
            parameters=parameters,
            collection=self.collection,
            model=self.model,
            validation_model=self.validation,
            fields=fields,
        )
        serializer = self.model_serializer(data=result, many=True)
        self.validate_serializer(serializer)
        return serializer.data

    def save(self, data):
        serializer = self.save_serializer(data=data)
        self.validate_serializer(serializer)
        result = db.save_single(
            post_data=serializer.data,
            collection=self.collection,
            model=self.model,
            validation_model=self.validation,
        )
        serializer = self.response_serializer(data=result)
        self.validate_serializer(serializer)
        return serializer.data

    def update(self, uuid, data):
        serializer = self.update_serializer(data=data)
        self.validate_serializer(serializer)
        result = db.update_single(
            uuid=uuid,
            put_data=serializer.data,
            collection=self.collection,
            model=self.model,
            validation_model=self.validation,
        )
        serializer = self.model_serializer(data=result)
        self.validate_serializer(serializer)
        return serializer.data

    def update_nested(self, uuid, field, data, params=None):
        return db.update_nested_single(
            uuid=uuid,
            field=field,
            put_data=data,
            collection=self.collection,
            model=self.model,
            validation_model=self.validation,
            params=params,
        )

    def push_nested(self, uuid, field, data, params=None):
        return db.push_nested_item(
            uuid=uuid,
            field=field,
            put_data=data,
            collection=self.collection,
            model=self.model,
            validation_model=self.validation,
            params=params,
        )

    def exists(self, parameters=None):
        return db.exists(
            parameters=parameters,
            collection=self.collection,
            model=self.model,
            validation_model=self.validation,
        )


class CampaignService(DBService):
    def __init__(self):
        return super().__init__(
            collection="campaign",
            model=campaign_models.GoPhishCampaignsModel,
            validation=campaign_models.validate_campaign,
            model_serializer=campaign_serializers.GoPhishCampaignsSerializer,
            response_serializer=campaign_serializers.GoPhishCampaignsResponseSerializer,
            save_serializer=campaign_serializers.GoPhishCampaignsPostSerializer,
            update_serializer=campaign_serializers.GoPhishCampaignsPatchSerializer,
        )


class LandingPageService(DBService):
    def __init__(self):
        return super().__init__(
            collection="landing_page",
            model=landing_page_models.LandingPageModel,
            validation=landing_page_models.validate_landing_page,
            model_serializer=landing_page_serializers.LandingPageSerializer,
            response_serializer=landing_page_serializers.LandingPageResponseSerializer,
            save_serializer=landing_page_serializers.LandingPagePostSerializer,
            update_serializer=landing_page_serializers.LandingPagePatchSerializer,
        )

    def clear_and_set_default(self, uuid):
        db_url = db.get_mongo_uri()
        client = pymongo.MongoClient(db_url)
        collection = client["pca_data_dev"]["landing_page"]
        sub_query = {}
        newvalues = {"$set": {"is_default_template": False}}
        collection.update_many(sub_query, newvalues)
        sub_query = {"landing_page_uuid": uuid}
        newvalues = {"$set": {"is_default_template": True}}
        collection.update_one(sub_query, newvalues)


class SubscriptionService(DBService):
    def __init__(self):
        self.campaign_service = CampaignService()
        return super().__init__(
            collection="subscription",
            model=subscription_models.SubscriptionModel,
            validation=subscription_models.validate_subscription,
            model_serializer=subscriptions_serializers.SubscriptionSerializer,
            response_serializer=subscriptions_serializers.SubscriptionDeleteResponseSerializer,
            save_serializer=subscriptions_serializers.SubscriptionPostSerializer,
            update_serializer=subscriptions_serializers.SubscriptionPatchSerializer,
        )

    def get(self, uuid):
        subscription = db.get_single(
            uuid=uuid,
            collection=self.collection,
            model=self.model,
            validation_model=self.validation,
        )
        subscription["gophish_campaign_list"] = self.campaign_service.get_list(
            {"subscription_uuid": uuid}
        )
        serializer = self.get_serializer(data=subscription)
        self.validate_serializer(serializer)
        return serializer.data

    def get_single_subscription_webhook(self, campaign_id):
        return db.get_single_subscription_webhook(
            campaign_id, self.collection, self.model, self.validation
        )


class RecommendationService(DBService):
    def __init__(self):
        return super().__init__(
            collection="recommendations",
            model=recommendations_models.RecommendationsModel,
            validation=recommendations_models.validate_recommendations,
            model_serializer=recommendations_serializers.RecommendationsSerializer,
            response_serializer=recommendations_serializers.RecommendationsResponseSerializer,
            save_serializer=recommendations_serializers.RecommendationsPostSerializer,
            update_serializer=recommendations_serializers.RecommendationsPatchSerializer,
        )


class TemplateService(DBService):
    def __init__(self):
        return super().__init__(
            collection="template",
            model=template_models.TemplateModel,
            validation=template_models.validate_template,
            model_serializer=template_serializers.TemplateSerializer,
            response_serializer=template_serializers.TemplateResponseSerializer,
            save_serializer=template_serializers.TemplatePostSerializer,
            update_serializer=template_serializers.TemplatePatchSerializer,
        )


class TagService(DBService):
    def __init__(self):
        return super().__init__(
            collection="tag_definition",
            model=tag_models.TagModel,
            validation=tag_models.validate_tag,
            model_serializer=tag_serializers.TagSerializer,
            response_serializer=tag_serializers.TagResponseSerializer,
            save_serializer=tag_serializers.TagPostSerializer,
            update_serializer=tag_serializers.TagPatchSerializer,
        )


class DHSContactService(DBService):
    def __init__(self):
        return super().__init__(
            collection="dhs_contact",
            model=dhs_models.DHSContactModel,
            validation=dhs_models.validate_dhs_contact,
            model_serializer=dhs_serializers.DHSContactSerializer,
            response_serializer=dhs_serializers.DHSContactResponseSerializer,
            save_serializer=dhs_serializers.DHSContactPostSerializer,
            update_serializer=dhs_serializers.DHSContactPatchSerializer,
        )


class CustomerService(DBService):
    def __init__(self):
        return super().__init__(
            collection="customer",
            model=customer_models.CustomerModel,
            validation=customer_models.validate_customer,
            model_serializer=customer_serializers.CustomerSerializer,
            response_serializer=customer_serializers.CustomerResponseSerializer,
            save_serializer=customer_serializers.CustomerPostSerializer,
            update_serializer=customer_serializers.CustomerPatchSerializer,
        )


class TargetHistoryService(DBService):
    def __init__(self):
        return super().__init__(
            collection="target",
            model=target_history_models.TargetHistoryModel,
            validation=target_history_models.validate_history,
            model_serializer=target_history_serializers.TargetHistorySerializer,
            response_serializer=target_history_serializers.TargetHistoryResponseSerializer,
            save_serializer=target_history_serializers.TargetHistoryPostSerializer,
            update_serializer=target_history_serializers.TargetHistoryPatchSerializer,
        )
