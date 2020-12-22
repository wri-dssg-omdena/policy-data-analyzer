import os

import pandas as pd
import plotly.express as px

if __name__ == "__main__":
    dataset_dir = "data/processed/2020-10-24"
    # Read data produced by scraping team
    scraping_metadata = pd.read_csv(
        os.path.join(dataset_dir, "scraping_metadata.csv"),
        sep=",",
        error_bad_lines=False,
        parse_dates=["publication_date"]
    )
    scraping_metadata = scraping_metadata[
        scraping_metadata["publication_date"].notnull()
    ]
    # Group publication dates by month
    scraping_metadata["publication_month"] = scraping_metadata[
        "publication_date"
        ].apply(lambda x: pd.Timestamp(str(x.year) + "-" + str(x.month)))
    scraping_timeline = scraping_metadata\
        .groupby(["country", "publication_month"])\
        .count()["id"]\
        .reset_index()
    fig = px.line(
        scraping_timeline,
        x="publication_month",
        y="id",
        color='country',
        labels={
            "publication_month": "Publication Date",
            "country": "Country",
            "id": "Number of Scraped Policy Documents"
        }
    )
    fig.show()