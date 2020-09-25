from faker import Faker


class FakerUtil:
    """Faker Util Classes

        Used for creating Faker instances and genration of fake data.

    Args:
        object (Faker): Faker class object with callable faker options
    """

    def __init__(self):
        """init"""
        self.fake = Faker()
        self.address = self.Address(self.fake)
        self.automotive = self.Automotive(self.fake)
        self.color = self.Color(self.fake)
        self.company = self.Company(self.fake)
        self.credit_card = self.CreditCard(self.fake)
        self.currency = self.Currency(self.fake)
        self.file = self.File(self.fake)
        self.internet = self.Internet(self.fake)
        self.isbn = self.Isbn(self.fake)
        self.job = self.Job(self.fake)
        self.file = self.File(self.fake)
        self.lorem = self.Lorem(self.fake)
        self.person = self.Person(self.fake)
        self.phone = self.Phone(self.fake)

    class Address:
        """Address

        Faker Gererated Address
        Learn more at: https://faker.readthedocs.io/en/stable/providers/faker.providers.address.html
        """

        def __init__(self, faker):
            """[summary]

            Args:
                faker (Faker): Faker import
            """
            self.fake = faker

        def address(self):
            """address"""
            return self.fake.address()

        def building_number(self):
            """building_number"""
            return self.fake.building_number()

        def city(self):
            """city"""
            return self.fake.city()

        def city_suffix(self):
            """city_suffix"""
            return self.fake.city_suffix()

        def country(self):
            """country"""
            return self.fake.country()

        def country_code(self):
            """country_code"""
            return self.fake.country_code()

        def postcode(self):
            """postcode"""
            return self.fake.postcode()

        def street_address(self):
            """street_address"""
            return self.fake.street_address()

        def street_name(self):
            """street_name"""
            return self.fake.street_name()

        def street_suffix(self):
            """street_suffix"""
            return self.fake.street_suffix()

    class Automotive:
        """Automotive

        https://faker.readthedocs.io/en/stable/providers/faker.providers.automotive.html
        """

        def __init__(self, faker):
            """init"""
            self.fake = faker

        def license_plate(self):
            """license_plate"""
            return self.fake.license_plate()

    class Color:
        """Color

        https://faker.readthedocs.io/en/stable/providers/faker.providers.color.html
        """

        def __init__(self, faker):
            """init"""
            self.fake = faker

        def color(self):
            """color"""
            return self.fake.color()

        def color_name(self):
            """color name"""
            return self.fake.color_name()

        def hex_color(self):
            """hex color"""
            return self.fake.hex_color()

        def rgb_color(self):
            """rgb color"""
            return self.fake.rgb_color()

        def rgb_css_color(self):
            """rgb css color"""
            return self.fake.rgb_css_color()

        def safe_color_name(self):
            """safe color name"""
            return self.fake.safe_color_name()

        def safe_hex_color(self):
            """safe hex color"""
            return self.fake.safe_hex_color()

    class Company:
        """Company

        https://faker.readthedocs.io/en/stable/providers/faker.providers.company.html
        """

        def __init__(self, faker):
            """init"""
            self.fake = faker

        def bs(self):
            """bs"""
            return self.fake.bs()

        def catch_phrase(self):
            """catch phrase"""
            return self.fake.catch_phrase()

        def company(self):
            """company"""
            return self.fake.company()

        def company_suffix(self):
            """company suffix"""
            return self.fake.company_suffix()

    class CreditCard:
        """CreditCard

        https://faker.readthedocs.io/en/stable/providers/faker.providers.credit_card.html
        """

        def __init__(self, faker):
            """init"""
            self.fake = faker

        def credit_card_expire(self):
            """credit_card_expire"""
            return self.fake.credit_card_expire()

        def credit_card_full(self):
            """credit_card_full"""
            return self.fake.credit_card_full()

        def credit_card_number(self):
            """credit_card_number"""
            return self.fake.credit_card_number()

        def credit_card_provider(self):
            """credit_card_provider"""
            return self.fake.credit_card_provider()

        def credit_card_security_code(self):
            """credit_card_security_code"""
            return self.fake.credit_card_security_code()

    class Currency:
        """Currency

        https://faker.readthedocs.io/en/stable/providers/faker.providers.currency.html
        """

        def __init__(self, faker):
            """init"""
            self.fake = faker

        def cryptocurrency_name(self):
            """cryptocurrency_name"""
            return self.fake.cryptocurrency_name()

        def cryptocurrency_code(self):
            """cryptocurrency_code"""
            return self.fake.cryptocurrency_code()

        def currency_code(self):
            """currency_code"""
            return self.fake.currency_code()

        def currency_name(self):
            """currency_name"""
            return self.fake.currency_name()

        def currency_symbol(self):
            """currency_symbol"""
            return self.fake.currency_symbol()

    class File:
        """File

        https://faker.readthedocs.io/en/stable/providers/faker.providers.file.html
        """

        def __init__(self, faker):
            self.fake = faker

        def file_extension(self, category=None):
            """file_extension

            Args:
                category (audio|image|office|text|video, optional): optional random video extention. Defaults to None.

            """
            return self.fake.file_extension(category=category)

        def file_name(self, category=None, extension=None):
            """
            category – audio|image|office|text|video
            extension – file extension

            """
            return self.fake.file_name(category=category, extension=extension)

        def file_path(self, depth=1, category=None, extension=None):
            """[summary]

            Args:
                depth (int, optional): [description]. Defaults to 1.
                category (audio|image|office|text|video, optional): Random category. Defaults to None.
                extension (string, optional): custom extention. Defaults to None.

            """
            return self.fake.file_path(
                depth=depth, category=category, extension=extension
            )

        def mime_type(self):
            """mine_type"""
            return self.fake.mime_type()

        def unix_device(self):
            """unix_device"""
            return self.fake.unix_device()

        def unix_partition(self):
            """unix_partition"""
            return self.fake.unix_partition()

    class Internet:
        """Internet

        https://faker.readthedocs.io/en/stable/providers/faker.providers.internet.html
        """

        def __init__(self, faker):
            """init"""
            self.fake = faker

        def ascii_company_email(self):
            """ascii_company_email"""
            return self.fake.ascii_company_email()

        def ascii_email(self):
            """ascii_email"""
            return self.fake.ascii_email()

        def ascii_free_email(self):
            """ascii_free_email"""
            return self.fake.ascii_free_email()

        def ascii_safe_email(self):
            """ascii_safe_email"""
            return self.fake.ascii_safe_email()

        def company_email(self):
            """company_email"""
            return self.fake.company_email()

        def domain_name(self, levels=1):
            """domain_name"""
            return self.fake.domain_name(levels=levels)

        def email(self, domain=None):
            """email"""
            return self.fake.email(domain=domain)

        def free_email(self):
            """free_email"""
            return self.fake.free_email()

        def free_email_domain(self):
            """free_email_domain"""
            return self.fake.free_email_domain()

        def hostname(self, levels=1):
            """hostname"""
            return self.fake.hostname(levels=levels)

        def image_url(self):
            """image_url"""
            return self.fake.image_url()

        def ipv4(self, network=False, address_class=None, private=None):
            """ipv4"""
            return self.fake.ipv4(
                network=network, address_class=address_class, private=private
            )

        def ipv6(self):
            """ipv6"""
            return self.fake.ipv6()

        def mac_address(self):
            """mac_address"""
            return self.fake.mac_address()

        def user_name(self):
            """user_name"""
            return self.fake.user_name()

        def url(self):
            """url"""
            return self.fake.url()

        def uri(self):
            """uri"""
            return self.fake.uri()

        def safe_email(self):
            """safe_email"""
            return self.fake.safe_email()

        def safe_domain_name(self):
            """safe_domain_name"""
            return self.fake.safe_domain_name()

    class Isbn:
        """Isbn

        https://faker.readthedocs.io/en/stable/providers/faker.providers.isbn.html
        """

        def __init__(self, faker):
            """init"""
            self.fake = faker

        def isbn10(self, separator="-"):
            """isbn10"""
            return self.fake.isbn10(separator=separator)

        def isbn13(self, separator="-"):
            """isbn13"""
            return self.fake.isbn13(separator=separator)

    class Job:
        """Job

        https://faker.readthedocs.io/en/stable/providers/faker.providers.job.html
        """

        def __init__(self, faker):
            """init"""
            self.fake = faker

        def position(self):
            """position"""
            return self.fake.job()

    class Lorem:
        """Lorem

        https://faker.readthedocs.io/en/stable/providers/faker.providers.lorem.html
        """

        def __init__(self, faker):
            """init"""
            self.fake = faker

        def paragraph(self):
            """paragraph"""
            return self.fake.paragraph()

        def sentence(self):
            """sentence"""
            return self.fake.sentence()

        def text(self):
            """text"""
            return self.fake.text()

    class Person:
        """Person

        https://faker.readthedocs.io/en/stable/providers/faker.providers.person.html
        """

        def __init__(self, faker):
            """init"""
            self.fake = faker

        def first_name(self):
            """first_name"""
            return self.fake.first_name()

        def first_name_female(self):
            """first_name_female"""
            return self.fake.first_name_female()

        def first_name_male(self):
            """first_name_male"""
            return self.fake.first_name_male()

        def first_name_nonbinary(self):
            """first_name_nonbinary"""
            return self.fake.first_name_nonbinary()

        def language_name(self):
            """language_name"""
            return self.fake.language_name()

        def last_name(self):
            """last_name"""
            return self.fake.last_name()

        def last_name_female(self):
            """last_name_female"""
            return self.fake.last_name_female()

        def last_name_male(self):
            """last_name_male"""
            return self.fake.last_name_male()

        def last_name_nonbinary(self):
            """last_name_nonbinary"""
            return self.fake.last_name_nonbinary()

        def name(self):
            """name"""
            return self.fake.name()

        def name_female(self):
            """name_female"""
            return self.fake.name_female()

        def name_male(self):
            """name_male"""
            return self.fake.name_male()

        def name_nonbinary(self):
            """name_nonbinary"""
            return self.fake.name_nonbinary()

        def prefix(self):
            """prefix"""
            return self.fake.prefix()

        def prefix_female(self):
            """prefix_female"""
            return self.fake.prefix_female()

        def prefix_male(self):
            """prefix_male"""
            return self.fake.prefix_male()

        def prefix_nonbinary(self):
            """prefix_nonbinary"""
            return self.fake.prefix_nonbinary()

        def suffix(self):
            """suffix"""
            return self.fake.suffix()

        def suffix_female(self):
            """suffix_female"""
            return self.fake.suffix_female()

        def suffix_male(self):
            """suffix_male"""
            return self.fake.suffix_male()

        def ssn(self):
            """ssn"""
            return self.fake.ssn()

    class Phone:
        """Phone

        https://faker.readthedocs.io/en/stable/providers/faker.providers.phone_number.html
        """

        def __init__(self, faker):
            """init"""
            self.fake = faker

        def country_calling_code(self):
            """country_calling_code"""
            return self.fake.country_calling_code()

        def phone_number(self):
            """phone_number"""
            return self.fake.phone_number()

        def msisdn(self):
            """msisdn"""
            return self.fake.msisdn()
