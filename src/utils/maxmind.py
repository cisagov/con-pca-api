"""Maxmind database utils."""
# Standard Python Libraries
import logging

# Third-Party Libraries
import geoip2.database
import geoip2.errors


def get_asn_org(ip_address):
    """Get asn org from maxmind database."""
    try:
        with geoip2.database.Reader("GeoLite2-ASN.mmdb") as reader:
            return reader.asn(ip_address).autonomous_system_organization
    except geoip2.errors.AddressNotFoundError:
        logging.info(f"{ip_address} not found in maxmind database.")
        return None
    except Exception as e:
        logging.exception(e)
        return None


def get_city_country(ip_address):
    """Get city from maxmind database."""
    try:
        with geoip2.database.Reader("GeoLite2-City.mmdb") as reader:
            response = reader.city(ip_address)
            return response.city.name, response.country.name
    except geoip2.errors.AddressNotFoundError:
        logging.info(f"{ip_address} not found in maxmind database.")
        return None, None
    except Exception as e:
        logging.exception(e)
        return None, None
