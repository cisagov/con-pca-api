"""Customer views."""
# Standard Python Libraries
from collections import OrderedDict

# Third-Party Libraries
from flask import jsonify, request
from flask.views import MethodView

# cisagov Libraries
from api.manager import CustomerManager, SubscriptionManager
from utils.sectors import SECTORS

customer_manager = CustomerManager()
subscription_manager = SubscriptionManager()


class CustomersView(MethodView):
    """CustomersView."""

    def get(self):
        """Get."""
        if "archived" not in request.args:
            return jsonify(customer_manager.all())
        else:
            parameters = customer_manager.get_query(request.args)
            parameters["archived"] = {"$in": [False, None]}
            if request.args.get("archived", "").lower() == "true":
                parameters["archived"] = True

            return jsonify(customer_manager.all(params=parameters))

    def post(self):
        """Post."""
        data = request.json
        return jsonify(customer_manager.save(data))


class CustomerView(MethodView):
    """CustomerView."""

    def get(self, customer_id):
        """Get."""
        return jsonify(customer_manager.get(document_id=customer_id))

    def put(self, customer_id):
        """Put."""
        customer_manager.update(document_id=customer_id, data=request.json)
        return jsonify({"success": True})

    def delete(self, customer_id):
        """Delete."""
        subscriptions = subscription_manager.all(
            params={"customer_id": customer_id},
            fields=["_id", "name"],
        )
        if subscriptions:
            return (
                jsonify(
                    {
                        "error": "Customer has active subscriptions.",
                        "subscriptions": subscriptions,
                    }
                ),
                400,
            )
        customer_manager.delete(document_id=customer_id)
        return jsonify({"success": True})


class ArchiveCustomerView(MethodView):
    """ArchiveCustomerView."""

    def put(self, customer_id):
        """Put."""
        active_subs = subscription_manager.count(
            {"status": {"$in": ["queued", "running"]}, "customer_id": customer_id}
        )
        if active_subs == 0:
            customer_manager.update(document_id=customer_id, data=request.json)
            return jsonify({"success": True})
        else:
            return jsonify({"success": False})


class CustomerCountView(MethodView):
    """CustomerCountView."""

    def get(self):
        """Get the count of customers."""
        parameters = dict(request.args)
        parameters = subscription_manager.get_query(parameters)

        # if request.args.get("template"):
        #     cycles = cycle_manager.all(
        #         params={"template_ids": request.args["template"]},
        #         fields=["subscription_id"],
        #     )
        #     subscription_ids = list({c["subscription_id"] for c in cycles})
        #     parameters["$or"] = [
        #         {"_id": {"$in": subscription_ids}},
        #         {"templates_selected": request.args["template"]},
        #     ]

        if "archived" in request.args:
            archived = [
                {"archived": True},
            ]
        else:
            archived = [{"archived": {"$exists": False}}, {"archived": False}]

        if request.args.get("archived", "").lower() == "true":
            parameters["archived"] = True

        pipeline = [
            {
                "$addFields": {"customer_id": {"$toString": "$_id"}},
            }
        ]

        filter_val = request.args.get("searchFilter")
        if request.args.get("searchFilter"):
            filter_val = request.args.get("searchFilter")
            pipeline.insert(
                2,
                {
                    "$match": {
                        "$and": [
                            {
                                "$or": [
                                    {"name": {"$regex": filter_val, "$options": "i"}},
                                    {
                                        "identifier": {
                                            "$regex": filter_val,
                                            "$options": "i",
                                        }
                                    },
                                    {
                                        "stakeholder_shortname": {
                                            "$regex": filter_val,
                                            "$options": "i",
                                        }
                                    },
                                    {
                                        "address_1": {
                                            "$regex": filter_val,
                                            "$options": "i",
                                        }
                                    },
                                    {
                                        "address_2": {
                                            "$regex": filter_val,
                                            "$options": "i",
                                        }
                                    },
                                    {"city": {"$regex": filter_val, "$options": "i"}},
                                    {"state": {"$regex": filter_val, "$options": "i"}},
                                    {
                                        "zip_code": {
                                            "$regex": filter_val,
                                            "$options": "i",
                                        }
                                    },
                                ]
                            },
                            {"$or": archived},
                        ]
                    }
                },
            )
        else:
            pipeline.insert(
                2,
                {"$match": {"$or": archived}},
            )

        customerCount = len(
            customer_manager.page(
                params=pipeline,
            )
        )

        return str(customerCount)


class CustomersPagedView(MethodView):
    """Subscriptions Paged View."""

    def get(self, page, pagesize, sortby, sortorder):
        """Get."""
        parameters = dict(request.args)
        parameters = subscription_manager.get_query(parameters)

        sortdirection = 1
        if sortorder == "desc":
            sortdirection = -1

        sort_dict = OrderedDict()
        if sortby != "name" or sortby != "name_lower":
            sort_dict[sortby] = sortdirection
            sort_dict["name_lower"] = 1
        else:
            sort_dict["name_lower"] = sortdirection

        if "archived" in request.args:
            archived = [
                # { "archived": True  },
                {"archived": True},
            ]
        else:
            archived = [{"archived": {"$exists": False}}, {"archived": False}]

        if request.args.get("archived", "").lower() == "true":
            parameters["archived"] = True

        pipeline = [
            {
                "$addFields": {
                    "customer_id": {"$toString": "$_id"},
                    "name_lower": {"$toLower": "$name"},
                    "identifier_lower": {"$toLower": "$identifier"},
                    "stakeholder_shortname_lower": {
                        "$toLower": "$stakeholder_shortname"
                    },
                    "address_1_lower": {"$toLower": "$address_1"},
                    "address_2_lower": {"$toLower": "$address_2"},
                    "city_lower": {"$toLower": "$city_lower"},
                },
            },
            {"$sort": sort_dict},
            {"$skip": int(page) * int(pagesize)},
            {"$limit": int(pagesize)},
            {
                "$project": {
                    "_id": "$_id",
                    "name": "$name",
                    "identifier": "$identifier",
                    "stakeholder_shortname": "$stakeholder_shortname",
                    "address_1": "$address_1",
                    "address_2": "$address_2",
                    "city": "$city",
                    "state": "$state",
                    "zip_code": "$zip_code",
                }
            },
        ]

        filter_val = request.args.get("searchFilter")
        if request.args.get("searchFilter"):
            filter_val = request.args.get("searchFilter")
            pipeline.insert(
                2,
                {
                    "$match": {
                        "$and": [
                            {
                                "$or": [
                                    {
                                        "name_lower": {
                                            "$regex": filter_val,
                                            "$options": "i",
                                        }
                                    },
                                    {
                                        "identifier": {
                                            "$regex": filter_val,
                                            "$options": "i",
                                        }
                                    },
                                    {
                                        "stakeholder_shortname": {
                                            "$regex": filter_val,
                                            "$options": "i",
                                        }
                                    },
                                    {
                                        "address_1": {
                                            "$regex": filter_val,
                                            "$options": "i",
                                        }
                                    },
                                    {
                                        "address_2": {
                                            "$regex": filter_val,
                                            "$options": "i",
                                        }
                                    },
                                    {"city": {"$regex": filter_val, "$options": "i"}},
                                    {"state": {"$regex": filter_val, "$options": "i"}},
                                    {
                                        "zip_code": {
                                            "$regex": filter_val,
                                            "$options": "i",
                                        }
                                    },
                                ]
                            },
                            {"$or": archived},
                        ]
                    }
                },
            )
        else:
            pipeline.insert(
                2,
                {"$match": {"$or": archived}},
            )

        customers = customer_manager.page(
            params=pipeline,
        )

        return jsonify(customers)


class CustomersPOCView(MethodView):
    """CustomersPOCView."""

    def get(self):
        """Get."""
        customers = customer_manager.all()
        POCs = []
        for customer in customers:
            active_subscriptions = subscription_manager.all(
                params={
                    "customer_id": customer.get("_id"),
                    "status": {"$in": ["queued", "running"]},
                },
                fields=["_id", "name"],
            )
            for contact in customer.get("contact_list"):
                contact["company_name"] = customer.get("name")
                contact["active_subscriptions"] = (
                    True if active_subscriptions else False
                )

                contact.pop("active", None)
                POCs.append(contact)

        return jsonify(POCs)


class SectorIndustryView(MethodView):
    """SectorIndustryView."""

    def get(self):
        """Get."""
        return jsonify(SECTORS)
