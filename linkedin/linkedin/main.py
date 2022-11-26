import argparse
from logging import DEBUG

from dynaconf import Dynaconf, Validator
from linkedin_api import Linkedin
from sqlalchemy import create_engine
from sqlalchemy.orm import Session
from sqlalchemy.orm import sessionmaker

from glogger import getLogger as get_logger
from linkedin import models
from linkedin import raw_stocks


def get_db(user: str, password: str, name: str, host: str, port: int) -> Session:
    info = {
        "user": user,
        "pw": password,
        "db": name,
        "host": host,
        "port": port,
    }
    sqlalchemy_database_url = (
        "postgresql://%(user)s:%(pw)s@%(host)s:%(port)s/%(db)s" % info
    )
    engine = create_engine(sqlalchemy_database_url)
    local_session = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    return local_session()


logger = get_logger("main", level=DEBUG)

to_del = [
    "Ordinary Share",
    "Inc. Common Stock",
    "Common Stock",
]


def clean_name(name: str) -> str:
    for td in to_del:
        name = name.replace(td, "").strip()
    if name[-1] == ",":
        name = name[:-1].strip()
    return name


def main():
    parser = argparse.ArgumentParser(description="Run crawler")
    parser.add_argument(
        "--config", "-c", type=str, help="Path to config file", default="settings.toml"
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
        ],
    )
    db = get_db(settings.db_user, settings.db_password, settings.db_name, settings.db_host, settings.db_port)
    api = Linkedin(settings.linkedin_username, settings.linkedin_password)
    stocks = raw_stocks.get_raw_stocks()
    for symbol, name in stocks[3:20]:
        name = clean_name(name)
        logger.info("symbol: %s, name: %s", symbol, name)
        companies = api.search_companies(name, limit=1)
        if not len(companies):
            logger.error("Could not find company %s", name)
            continue

        company = companies[0]

        logger.info(
            "Found company (for %s) --- name: %s --- headline: %s --- subline: %s",
            name,
            company["name"],
            company["headline"],
            company["subline"],
        )

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
        db.commit()

        logger.debug("Adding locations")
        for loc in data["confirmedLocations"]:
            db.add(
                models.Locations(
                    company_urn_id=urn_id,
                    country=loc["country"],
                    geographic_area=loc["geographicArea"],
                    city=loc["city"],
                    postal_code=loc["postalCode"],
                    line=loc["line1"],
                    headquarter=loc["headquarter"],
                )
            )
        db.commit()

        companies_urn = [company["urn_id"]]
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

        for person in people:
            logger.debug("Getting info of %s", person)
            profile = api.get_profile(urn_id=person["urn_id"])
            logger.debug("data: %s", profile)
            db.add(
                models.People(
                    industry_name=profile["industryName"],
                    first_name=profile["firstName"],
                    last_name=profile["lastName"],
                    student=profile["student"],
                    country=profile["geoCountryName"],
                    city=profile.get("geoLocationName", None),
                )
            )
            logger.debug("data: %s", profile["education"])
            for edu in profile["education"]:
                tp = edu.get("timePeriod", None)
                start = tp.get("startDate", None) if tp else None
                end = tp.get("endDate", None) if tp else None
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
            logger.debug("data: %s", profile["experience"])
            for exp in profile["experience"]:
                tp = exp.get("timePeriod", None)
                start = tp.get("startDate", None) if tp else None
                end = tp.get("endDate", None) if tp else None
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
        db.commit()


# https://github.com/tomquirk/linkedin-api
# https://nubela.co/proxycurl/linkedin
if __name__ == "__main__":
    main()
