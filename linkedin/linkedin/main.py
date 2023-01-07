import argparse
from logging import DEBUG

from dynaconf import Dynaconf
from dynaconf import Validator
from linkedin_api import Linkedin
from requests.cookies import cookiejar_from_dict
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from glogger import getLogger as get_logger
from linkedin import models
from linkedin import raw_stocks


def get_db(settings: Dynaconf) -> Session:
    info = {
        "host": settings.db_host,
        "port": settings.db_port,
        "db": settings.db_name,
        "user": settings.db_user,
        "pw": settings.db_password,
    }
    sqlalchemy_database_url = (
        "postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s" % info
    )
    engine = create_engine(sqlalchemy_database_url)
    local_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return local_session()


logger = get_logger("main", level=DEBUG)

suffix = [
    "Class A",
    "Global Limited",
    "Common Stock,",
    "Class A Common Stock,",
    "Agile Growth Corp. Warrant.",
    "Warrant",
    "Common Shares",
    "Acquisition",
    "SAIL Warrant.",
    "(Canada)",
    "(Bermuda)",
    "S.A.",
    "N.V. Common Stock",
    "(Holding Company) Common Stock",
    "Class A Common Stock New",
    "Class A Ordinary Shares",
    "PLC Ordinary Shares",
    "Ordinary Share",
    "Class A Common Stock",
    "(The) Common Stock",
    "Common Stock",
    "ADS",
    "ASA",
    "SE",
    "SA American Depositary Shares",
    "SA",
    "AG",
    "S.A. Sponsored ADR (Spain)",
    "Limited American Depositary Shares",
    "Class A Subordinate Voting Shares",
    "Depositary Shares",
    "PLC Common Stock",
    "(REIT)",
    "REIT",
    "American Depositary Shares",
    "(",
    "Corporation Class A Common Stock",
]
suffix = list(sorted(suffix, key=lambda x: len(x), reverse=True))
# to_del = list(map(str.lower, to_del))
# suffix = list(map(str.lower, suffix))

puncs = [
    ",",
    ".",
    "(",
    ")",
]


def clean(name: str) -> str:
    name = name.strip()
    for p in puncs:
        name = name.replace(p, "").strip()
    return name


def clean_name(name: str) -> str:
    name = clean(name)
    for s in suffix:
        idx = name.find(s)
        if idx != -1:
            name = clean(name[:idx])
    name = name.lower()
    for s in suffix:
        s = s.lower()
        if len(s) >= 5:
            idx = name.find(s)
            if idx != -1:
                name = clean(name[:idx])
    name = clean(name)
    return name


def parse() -> tuple[argparse.Namespace, Dynaconf]:
    parser = argparse.ArgumentParser(description="Run crawler")
    parser.add_argument(
        "--config", "-c", type=str, help="Path to config file", default="settings.toml"
    )
    parser.add_argument(
        "--cookie", action="store_true", help="Just show cookie and exit", default=False
    )
    args = parser.parse_args()
    config_path = args.config
    logger.info("config path: %s", config_path)
    settings = Dynaconf(
        envvar_prefix="LK",
        settings_files=[config_path],
        validators=[
            Validator("db_host", is_type_of=str),
            Validator("db_port", is_type_of=int),
            Validator("db_name", is_type_of=str),
            Validator("db_user", is_type_of=str),
            Validator("db_password", is_type_of=str),
            Validator("linkedin_username", is_type_of=str),
            Validator("linkedin_password", is_type_of=str),
            Validator("linkedin_jsessionip", is_type_of=str),
            Validator("linkedin_li_at", is_type_of=str),
        ],
    )
    settings.validators.validate()
    return args, settings


def get_api(settings: Dynaconf) -> Linkedin:
    if settings.get("linkedin_jsessionip", False):
        logger.info("Using cookies")
        cookies = cookiejar_from_dict(
            {
                "liap": "true",
                "li_at": settings.linkedin_li_at,
                "JSESSIONID": settings.linkedin_jsessionip,
            }
        )
        api = Linkedin("", "", cookies=cookies)
    else:
        logger.info("Using username and pass")
        logger.warning("It's better to use cookie to avoid login multiple times")
        api = Linkedin(settings.linkedin_username, settings.linkedin_password)
    return api


def find_company(api: Linkedin, name: str) -> dict | None:
    name = clean_name(name)
    companies = api.search_companies(name, limit=10)
    if not len(companies):
        logger.error("Could not find company %s", name)
        return None
    company = companies[0]
    logger.info(
        "Found company (for %s) --- name: %s --- headline: %s --- subline: %s",
        name,
        company["name"],
        company["headline"],
        company["subline"],
    )
    return company


def find_people(api: Linkedin, urn_id: str, data: dict) -> list:
    companies_urn = [urn_id]
    if "affiliatedCompaniesResolutionResults" in data:
        companies_urn.extend(
            [
                x["entityUrn"].split(":")[-1]
                for x in list(data["affiliatedCompaniesResolutionResults"].values())
            ]
        )
    logger.debug("%d affiliated companies", len(companies_urn))
    people = api.search_people(
        current_company=companies_urn, include_private_profiles=False
    )
    logger.info("Found %d people", len(people))
    return people


def add_locations(db: Session, urn_id: str, locations: list) -> None:
    logger.debug("Adding locations")
    for loc in locations:
        logger.debug("Loc:\n%s", loc)
        db.add(
            models.Locations(
                company_urn_id=urn_id,
                country=loc["country"],
                geographic_area=loc.get("geographicArea", None),
                city=loc["city"],
                postal_code=loc.get("postalCode", None),
                line=loc.get("line1", None),
                headquarter=loc["headquarter"],
            )
        )
    # db.commit()


def handle_experience(db: Session, exp: dict):
    tp = exp.get("timePeriod", None)
    start = tp.get("startDate", None) if tp else None
    end = tp.get("endDate", None) if tp else None
    logger.debug("Exp:\n%s", exp)
    db.add(
        models.Experience(
            location=exp.get("geoLocationName", None),
            company_name=exp["companyName"],
            company_urn=exp["companyUrn"].split(":")[-1]
            if "companyUrn" in exp
            else None,
            title=exp["title"],
            start=start,
            end=end,
        )
    )


def handle_education(db: Session, edu: dict):
    tp = edu.get("timePeriod", None)
    start = tp.get("startDate", None) if tp else None
    end = tp.get("endDate", None) if tp else None
    logger.debug("Edu:\n%s", edu)
    db.add(
        models.Education(
            degree=edu.get("degree", None),
            activities=edu.get("activities", None),
            name=edu["schoolName"],
            field=edu.get("fieldOfStudy", None),
            start=start,
            end=end,
        )
    )


def handle_person(person: dict, api: Linkedin, db: Session) -> None:
    logger.debug("Getting info of %s", person)
    profile = api.get_profile(urn_id=person["urn_id"])
    logger.debug("data:\n%s", profile)
    db.add(
        models.People(
            industry_name=profile.get("industryName", None),
            first_name=profile["firstName"],
            last_name=profile["lastName"],
            student=profile["student"],
            country=profile["geoCountryName"],
            city=profile.get("geoLocationName", None),
        )
    )
    logger.debug("data: %s", profile["education"])
    for edu in profile["education"]:
        handle_education(db, edu)
    logger.debug("data: %s", profile["experience"])
    for exp in profile["experience"]:
        handle_experience(db, exp)


def handle_stock(db: Session, api: Linkedin, symbol: str, name: str) -> None:
    logger.info("symbol: %s, name: %s", symbol, name)
    company = find_company(api, name)
    if not company:
        return
    urn_id = company["urn_id"]
    data = api.get_company(urn_id)
    logger.debug("Adding new company")
    db.add(
        models.Company(
            urn_id=urn_id,
            url=data["url"],
            staff_count=data["staffCount"],
            specialities=data["specialities"],
            name=data["universalName"],
            symbol=symbol,
        )
    )
    # db.commit()
    add_locations(db, urn_id, data["confirmedLocations"])
    people = find_people(api, company["urn_id"], data)
    for person in people:
        handle_person(person, api, db)
    # db.commit()


def main():
    args, settings = parse()
    db = get_db(settings)
    api = get_api(settings)
    if args.cookie:
        print("-----------------------")
        print(
            f"li_at:      {api.client.session.cookies.get('li_at')}\n"
            f"jsessionip: {api.client.session.cookies.get('JSESSIONID')}"
        )
        print("-----------------------")
        exit(0)
    stocks = raw_stocks.get_raw_stocks()
    for symbol, name in stocks[30:40]:
        handle_stock(db, api, symbol, name)


# https://github.com/tomquirk/linkedin-api
# https://nubela.co/proxycurl/linkedin
if __name__ == "__main__":
    main()
