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
        get_serializer,
        delete_response_serializer,
        save_serializer,
        save_response_serializer,
        update_serializer,
        update_response_serializer,
    ):
        self.collection = collection
        self.model = model
        self.validation = validation
        self.get_serializer = get_serializer
        self.delete_response_serializer = delete_response_serializer
        self.save_serializer = save_serializer
        self.save_response_serializer = save_response_serializer
        self.update_serializer = update_serializer
        self.update_response_serializer = update_response_serializer

    def delete(self, uuid):
        resp = db.delete_single(
            uuid=uuid,
            collection=self.collection,
            model=self.model,
            validation_model=self.validation,
        )
        serializer = self.delete_response_serializer(data=resp)
        serializer.is_valid()
        return serializer.data

    def get(self, uuid):
        result = db.get_single(
            uuid=uuid,
            collection=self.collection,
            model=self.model,
            validation_model=self.validation,
        )
        serializer = self.get_serializer(data=result)
        serializer.is_valid()
        return serializer.data

    def get_list(self, parameters=None, fields=None):
        result = db.get_list(
            parameters=parameters,
            collection=self.collection,
            model=self.model,
            validation_model=self.validation,
            fields=fields,
        )
        serializer = self.get_serializer(data=result, many=True)
        serializer.is_valid()
        return serializer.data

    def save(self, data):
        serializer = self.save_serializer(data=data)
        serializer.is_valid()
        result = db.save_single(
            post_data=serializer.data,
            collection=self.collection,
            model=self.model,
            validation_model=self.validation,
        )
        serializer = self.save_response_serializer(data=result)
        serializer.is_valid()
        return serializer.data

    def update(self, uuid, data):
        serializer = self.update_serializer(data=data)
        serializer.is_valid()
        result = db.update_single(
            uuid=uuid,
            put_data=serializer.data,
            collection=self.collection,
            model=self.model,
            validation_model=self.validation,
        )
        serializer = self.update_response_serializer(data=result)
        serializer.is_valid()
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
            get_serializer=campaign_serializers.GoPhishCampaignsSerializer,
            delete_response_serializer=campaign_serializers.GoPhishCampaignsResponseSerializer,
            save_serializer=campaign_serializers.GoPhishCampaignsPostSerializer,
            save_response_serializer=campaign_serializers.GoPhishCampaignsResponseSerializer,
            update_serializer=campaign_serializers.GoPhishCampaignsPatchSerializer,
            update_response_serializer=campaign_serializers.GoPhishCampaignsResponseSerializer,
        )


class LandingPageService(DBService):
    def __init__(self):
        return super().__init__(
            collection="landing_page",
            model=landing_page_models.LandingPageModel,
            validation=landing_page_models.validate_landing_page,
            get_serializer=landing_page_serializers.LandingPageSerializer,
            delete_response_serializer=landing_page_serializers.LandingPageResponseSerializer,
            save_serializer=landing_page_serializers.LandingPagePostSerializer,
            save_response_serializer=landing_page_serializers.LandingPageResponseSerializer,
            update_serializer=landing_page_serializers.LandingPagePatchSerializer,
            update_response_serializer=landing_page_serializers.LandingPageSerializer,
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
            get_serializer=subscriptions_serializers.SubscriptionSerializer,
            delete_response_serializer=subscriptions_serializers.SubscriptionDeleteResponseSerializer,
            save_serializer=subscriptions_serializers.SubscriptionPostSerializer,
            save_response_serializer=subscriptions_serializers.SubscriptionPostResponseSerializer,
            update_serializer=subscriptions_serializers.SubscriptionPatchSerializer,
            update_response_serializer=subscriptions_serializers.SubscriptionSerializer,
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
        return self.get_serializer(data=subscription).data

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
            get_serializer=recommendations_serializers.RecommendationsGetSerializer,
            delete_response_serializer=recommendations_serializers.RecommendationsDeleteResponseSerializer,
            save_serializer=recommendations_serializers.RecommendationsPostSerializer,
            save_response_serializer=recommendations_serializers.RecommendationsPostResponseSerializer,
            update_serializer=recommendations_serializers.RecommendationsPatchSerializer,
            update_response_serializer=recommendations_serializers.RecommendationsPatchResponseSerializer,
        )


class TemplateService(DBService):
    def __init__(self):
        return super().__init__(
            collection="template",
            model=template_models.TemplateModel,
            validation=template_models.validate_template,
            get_serializer=template_serializers.TemplateGetSerializer,
            delete_response_serializer=template_serializers.TemplateDeleteResponseSerializer,
            save_serializer=template_serializers.TemplatePostSerializer,
            save_response_serializer=template_serializers.TemplatePostResponseSerializer,
            update_serializer=template_serializers.TemplatePatchSerializer,
            update_response_serializer=template_serializers.TemplatePatchResponseSerializer,
        )


class TagService(DBService):
    def __init__(self):
        return super().__init__(
            collection="tag_definition",
            model=tag_models.TagModel,
            validation=tag_models.validate_tag,
            get_serializer=tag_serializers.TagSerializer,
            delete_response_serializer=tag_serializers.TagResponseSerializer,
            save_serializer=tag_serializers.TagPostSerializer,
            save_response_serializer=tag_serializers.TagResponseSerializer,
            update_serializer=tag_serializers.TagPatchSerializer,
            update_response_serializer=tag_serializers.TagSerializer,
        )


class DHSContactService(DBService):
    def __init__(self):
        return super().__init__(
            collection="dhs_contact",
            model=dhs_models.DHSContactModel,
            validation=dhs_models.validate_dhs_contact,
            get_serializer=dhs_serializers.DHSContactSerializer,
            delete_response_serializer=dhs_serializers.DHSContactResponseSerializer,
            save_serializer=dhs_serializers.DHSContactPostSerializer,
            save_response_serializer=dhs_serializers.DHSContactResponseSerializer,
            update_serializer=dhs_serializers.DHSContactPatchSerializer,
            update_response_serializer=dhs_serializers.DHSContactSerializer,
        )


class CustomerService(DBService):
    def __init__(self):
        return super().__init__(
            collection="customer",
            model=customer_models.CustomerModel,
            validation=customer_models.validate_customer,
            get_serializer=customer_serializers.CustomerSerializer,
            delete_response_serializer=customer_serializers.CustomerResponseSerializer,
            save_serializer=customer_serializers.CustomerPostSerializer,
            save_response_serializer=customer_serializers.CustomerResponseSerializer,
            update_serializer=customer_serializers.CustomerPatchSerializer,
            update_response_serializer=customer_serializers.CustomerSerializer,
        )


class TargetHistoryService(DBService):
    def __init__(self):
        return super().__init__(
            collection="target",
            model=target_history_models.TargetHistoryModel,
            validation=target_history_models.validate_history,
            get_serializer=target_history_serializers.TargetHistorySerializer,
            delete_response_serializer=target_history_serializers.TargetHistoryResponseSerializer,
            save_serializer=target_history_serializers.TargetHistoryPostSerializer,
            save_response_serializer=target_history_serializers.TargetHistoryResponseSerializer,
            update_serializer=target_history_serializers.TargetHistoryPatchSerializer,
            update_response_serializer=target_history_serializers.TargetHistorySerializer,
        )
