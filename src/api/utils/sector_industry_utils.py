"""sector_industry Utils file for api."""


def get_sectors_industries():
    """
    Get sectors and their associated industries

    Returns a list of all sectors and their associated industries

    Temporary Sector/Industry list hard coded on Barrys request. Can be added to
    a database location later for permanent storage and manipulation at a later date
    """
    sectors = [
        {
            "name": "Chemical",
            "industries": [
                {"name": "Other"},
                {"name": "Basic Chemicals"},
                {"name": "Specialty Products"},
                {"name": "Pharmaceutical Products"},
                {"name": "Consumer Products"},
                {"name": "Agricultural Products"},
            ],
        },
        {
            "name": "Commercial Facilities",
            "industries": [
                {"name": "Entertainment and Media"},
                {"name": "Gaming"},
                {"name": "Lodging"},
                {"name": "Other"},
                {"name": "Outdoor Events"},
                {"name": "Public Assembly"},
                {"name": "Real Estate"},
                {"name": "Retail"},
                {"name": "Sports Leagues"},
            ],
        },
        {
            "name": "Communications",
            "industries": [
                {"name": " Other"},
                {"name": " Telecommunications"},
                {"name": " Wireless Communications Service Providers"},
                {"name": " Broadcasting"},
                {"name": " Cable"},
                {"name": " Satellite"},
                {"name": " Wireline"},
            ],
        },
        {
            "name": "Critical Manufacturing",
            "industries": [
                {"name": "Electrical Equipment, Appliance and Component Manufacturing"},
                {"name": "Machinery Manufacturing"},
                {"name": "Other"},
                {"name": "Primary Metal Manufacturing"},
                {"name": "Transportation and Heavy Equipment Manufacturing"},
                {"name": "Manufacturing"},
                {"name": "Heavy Machinery Manufacturing"},
            ],
        },
        {
            "name": "Dams",
            "industries": [
                {"name": "Dams"},
                {"name": "Other"},
                {"name": "Private Hydropower Facilities in the US"},
                {"name": "Levees"},
                {"name": "Navigation Locks"},
                {"name": "Tailings and Waste Impoundments"},
            ],
        },
        {
            "name": "Defense Industrial Base",
            "industries": [
                {"name": "Aircraft Industry"},
                {"name": "Ammunition"},
                {"name": "Combat Vehicle"},
                {"name": "Communications"},
                {"name": "Defense Contractors   "},
                {"name": "Electrical Industry Commodities"},
                {"name": "Electronics"},
                {"name": "Mechanical Industry Commodities"},
                {"name": "Missile Industry"},
                {"name": "Other"},
                {"name": "Research and Development Facilities"},
                {"name": "Shipbuilding Industry"},
                {"name": "Space"},
                {"name": "Structural Industry Commodities"},
                {"name": "Troop Support"},
                {"name": "Weapons"},
            ],
        },
        {
            "name": "Emergency Services",
            "industries": [
                {"name": "Emergency Management"},
                {"name": "Emergency Medical Services"},
                {"name": "Fire and Rescue Services"},
                {"name": "Law Enforcement   "},
                {"name": "Other"},
                {"name": "Public Works"},
            ],
        },
        {
            "name": "Energy",
            "industries": [
                {"name": "Electric Power Generation, Transmission and Distribution"},
                {"name": "Natural Gas"},
                {"name": "Other"},
                {"name": "Petroleum Refineries"},
                {"name": "Oil and Natural Gas"},
            ],
        },
        {
            "name": "Financial Services",
            "industries": [
                {"name": "Other"},
                {"name": "US Banks"},
                {"name": "US Credit Unions"},
                {"name": "Consumer Services"},
                {"name": "Credit and Liquidity Products"},
                {"name": "Investment Products"},
                {"name": "Risk Transfer Products"},
            ],
        },
        {
            "name": "Food and Agriculture",
            "industries": [
                {"name": "Beverage Manufacturing Plants"},
                {"name": "Food Manufacturing Plants"},
                {"name": "Food Services"},
                {"name": "Other"},
                {"name": "Supply"},
                {"name": "Processing, Packaging, and Production"},
                {"name": "Product Storage"},
                {"name": "Product Transportation"},
                {"name": "Product Distribution"},
                {"name": "Supporting Facilities"},
            ],
        },
        {
            "name": "Government Facilities",
            "industries": [
                {"name": "Local Governments"},
                {"name": "Other"},
                {"name": "State Governments"},
                {"name": "Territorial Governments"},
                {"name": "Tribal Governments"},
                {"name": "Public Facilities"},
                {"name": "Non-Public Facilities"},
            ],
        },
        {
            "name": "Healthcare and Public Health",
            "industries": [
                {"name": "Hospitals"},
                {"name": "Other"},
                {"name": "Residential Care Facilities"},
                {"name": "Direct Patient Care"},
                {"name": "Health IT"},
                {"name": "Health Plans and Payers"},
                {"name": "Fatality Management Services"},
                {"name": "Medical Materials"},
                {"name": "Support Services"},
            ],
        },
        {
            "name": "Information Technology",
            "industries": [
                {"name": "Information Technology"},
                {"name": "Other"},
                {"name": "IT Production"},
                {"name": "DNS Services"},
                {"name": "Identity and Trust Support Management"},
                {"name": "Internet Content and Service Providers"},
                {"name": "Internet Routing and Connection"},
                {"name": "Incident Management"},
            ],
        },
        {
            "name": "Nuclear Reactors, Materials, and Waste",
            "industries": [
                {"name": "Operating Nuclear Power Plants"},
                {"name": "Other"},
                {"name": "Fuel Cycle Facilities"},
                {"name": "Nuclear Materials Transport"},
                {"name": "Radioactive Waste"},
                {"name": "Radioactive Materials"},
            ],
        },
        {
            "name": "Transportation Systems",
            "industries": [
                {"name": "Aviation"},
                {"name": "Freight Rail"},
                {"name": "Highway (truck transportation)"},
                {"name": "Maritime"},
                {"name": "Mass Transit and Passenger Rail"},
                {"name": "Municipalities with Traffic Control Systems"},
                {"name": "Other"},
                {
                    "name": "Pipelines (carries natural gas, hazardous liquids, and various chemicals.)"
                },
            ],
        },
        {
            "name": "Water and Wastewater Systems",
            "industries": [
                {"name": "Other"},
                {"name": "Public Water Systems"},
                {"name": "Publicly Owned Treatment Works"},
            ],
        },
    ]
    return sectors
