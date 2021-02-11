import os
import json
import argparse
from typing import Optional

import pandas as pd
import plotly.graph_objects as go
from fastapi import FastAPI, Response, Request
from fastapi.responses import FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles

from src.models.segment_highlighter import classes as highlighter_classes
from src.visualization.maps import plotly_map

# added by David #
import pandas as pd
import numpy as np
import dash
import dash_core_components as dcc
import dash_html_components as html
import dash_table
import dash_bootstrap_components as dbc
from urllib.request import urlopen
from dash.dependencies import Input, Output, State
import plotly.express as px
import json
import dash
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
import plotly.graph_objs as obj
import uvicorn as uvicorn
from dash.dependencies import Input, Output
from fastapi import FastAPI
from starlette.middleware.wsgi import WSGIMiddleware

# Configure module
highlighter_class = "sbert"
highlighter_id = "X"
highlighter_query = "beneficio económico"
highlighter_precision = 0.05
with open("src/visualization/app_config.json", "r") as f:
    config = json.load(f)

# Instantiate models
highlighter_class = highlighter_classes[highlighter_class]
highlighter = highlighter_class.load(highlighter_id)

app = FastAPI()

# Introduce templates and dependencies
templates = Jinja2Templates(directory="src/visualization/templates/")
app.mount("/assets", StaticFiles(directory="src/visualization/assets/"), name="assets")
app.mount("/data", StaticFiles(directory="data/"), name="data")

@app.get("/")
async def home(request: Request):
    return templates.TemplateResponse("home.html", {"request": request})

@app.get("/policies")
async def policies(request: Request, country_code: str, policy_basename: Optional[str] = None):
    # Populate list of policies
    with open("src/visualization/policy_row.html", "r") as f:
        row_template = f.read()
    policy_rows = ""
    for json_file in os.listdir(config[country_code]["json_dir"]):
        if not json_file.endswith(".json"):
            continue
        pdf_file = json_file.replace(".json", ".pdf")
        policy_rows += row_template.format(
            country_code = country_code,
            policy_title = json_file.replace(".json", ""),
            policy_basename = json_file,
            policy_path = os.path.join(config[country_code]["pdf_dir"], pdf_file)
        )
    highlight_rows = ""
    # Render highlights if requested
    if policy_basename is not None:
        highlights_path = os.path.join(
            config[country_code]["highlights_dir"],
            policy_basename.replace(".json", ".txt")
        )
        if os.path.exists(highlights_path):
            # Load precalculated highlights
            with open(highlights_path, "r") as f:
                highlight_rows = f.read()
        else:
            # Compute live if unavailable
            with open("src/visualization/highlight_row.html", "r") as f:
                row_template = f.read()
            policy_path = os.path.join(
                config[country_code]["json_dir"], policy_basename
            )
            with open(policy_path, "r", encoding="utf-8") as f:
                policy = json.load(f)
            highlights, _, pages = highlighter.highlight(
                policy, highlighter_query, highlighter_precision
            )
            for idx, highlight in enumerate(highlights):
                highlight = "<i>In page " + str(pages[idx]) + "</i>: " + highlight
                highlight_rows += row_template.format(highlight_text=highlight)
    return templates.TemplateResponse(
        "policies.html",
        {
            "request": request,
            "country_name": config[country_code]["country_name"],
            "policy_rows": policy_rows,
            "highlight_rows": highlight_rows
        }
    )

@app.get("/topics")
async def topics(request: Request):
    return templates.TemplateResponse(
        "topic_breakdown.html",
        {
            "request": request
        }
    )

@app.get("/country_matrix")
async def country_matrix(request: Request, country_code: str):
    coocurrences = pd.read_csv(config[country_code]["coocurrences_file"])
    coocurrences.columns = ["Incentive Instrument", "Land Type", "Count"]
    coocurrences = coocurrences.pivot(
        index="Incentive Instrument", columns="Land Type", values="Count"
    ).fillna(0)
    fig = go.Figure(data=go.Heatmap(
        y=coocurrences.index,
        x=coocurrences.columns,
        z=coocurrences,
        colorscale=["lightgrey", "green"],
        hovertemplate='Incentive Instrument: %{y}<br>Land Type: %{x}<br>Policies where they Co-Occur : %{z}<extra></extra>',
    ))
    fig.update_traces(showscale=False)
    fig.update_layout(
        margin={"t": 40, "b": 40, "r": 50, "l": 60}
    )
    return templates.TemplateResponse(
        "canvas.html",
        {
            "request": request,
            "content": fig.to_html()
        }
    )


@app.get("/map_technical_assistance")
async def map_technical_assistance(request: Request):
    with urlopen(
            'https://raw.githubusercontent.com/davidlararamos/mexico_geojson/master/latin_america.json') as response:
        latin_america = json.load(response)

    for feature in latin_america['features']:  # we are creating new keys for our dictionary
        feature['id'] = feature['properties']['sov_a3']

    lst = ['MEX', 'CHL', 'GTM', 'PER','SLV']
    lst2 = ['0.739130434782609', '1', '0.956521739130435','0.782608695652174', '0']

    df_latin_america = pd.DataFrame(list(zip(lst, lst2)),
                                    columns=['id', 'Normalized value'])
    df_latin_america['Normalized value'] = df_latin_america['Normalized value'].astype(float)

    fig = px.choropleth(df_latin_america, geojson=latin_america, locations=df_latin_america['id'],
                        color='Normalized value',color_continuous_scale="Viridis")
    fig.update_geos(fitbounds='locations', visible=False)

    return templates.TemplateResponse(       # templates = Jinja2Templates(directory="src/visualization/templates/")
        "map.html",
        {
            "request": request,
            "map_html": fig.to_html()
        }
    )

@app.get("/map_supplies")
async def map_supplies(request: Request):
    with urlopen(
            'https://raw.githubusercontent.com/davidlararamos/mexico_geojson/master/latin_america.json') as response:
        latin_america = json.load(response)

    for feature in latin_america['features']:  # we are creating new keys for our dictionary
        feature['id'] = feature['properties']['sov_a3']

    lst = ['MEX', 'CHL', 'GTM', 'PER','SLV']
    lst2 = ['0.483870967741935', '0.967741935483871', '1','0.548387096774194', '0']

    df_latin_america = pd.DataFrame(list(zip(lst, lst2)),
                                    columns=['id', 'Normalized value'])
    df_latin_america['Normalized value'] = df_latin_america['Normalized value'].astype(float)

    fig = px.choropleth(df_latin_america, geojson=latin_america, locations=df_latin_america['id'],
                        color='Normalized value',color_continuous_scale="Viridis")
    fig.update_geos(fitbounds='locations', visible=False)

    return templates.TemplateResponse(       # templates = Jinja2Templates(directory="src/visualization/templates/")
        "map.html",
        {
            "request": request,
            "map_html": fig.to_html()
        }
    )

@app.get("/map_guarantee")
async def map_guarantee(request: Request):
    with urlopen(
            'https://raw.githubusercontent.com/davidlararamos/mexico_geojson/master/latin_america.json') as response:
        latin_america = json.load(response)

    for feature in latin_america['features']:  # we are creating new keys for our dictionary
        feature['id'] = feature['properties']['sov_a3']

    lst = ['MEX', 'CHL', 'GTM', 'PER','SLV']
    lst2 = ['0.56', '0.4', '1','0.52', '0']

    df_latin_america = pd.DataFrame(list(zip(lst, lst2)),
                                    columns=['id', 'Normalized value'])
    df_latin_america['Normalized value'] = df_latin_america['Normalized value'].astype(float)

    fig = px.choropleth(df_latin_america, geojson=latin_america, locations=df_latin_america['id'],
                        color='Normalized value',color_continuous_scale="Viridis")
    fig.update_geos(fitbounds='locations', visible=False)

    return templates.TemplateResponse(       # templates = Jinja2Templates(directory="src/visualization/templates/")
        "map.html",
        {
            "request": request,
            "map_html": fig.to_html()
        }
    )

@app.get("/map_fine")
async def map_guarantee(request: Request):
    with urlopen(
            'https://raw.githubusercontent.com/davidlararamos/mexico_geojson/master/latin_america.json') as response:
        latin_america = json.load(response)

    for feature in latin_america['features']:  # we are creating new keys for our dictionary
        feature['id'] = feature['properties']['sov_a3']

    lst = ['MEX', 'CHL', 'GTM', 'PER','SLV']
    lst2 = ['0.23', '0.77', '1','0.46', '0']

    df_latin_america = pd.DataFrame(list(zip(lst, lst2)),
                                    columns=['id', 'Normalized value'])
    df_latin_america['Normalized value'] = df_latin_america['Normalized value'].astype(float)

    fig = px.choropleth(df_latin_america, geojson=latin_america, locations=df_latin_america['id'],
                        color='Normalized value',color_continuous_scale="Viridis")
    fig.update_geos(fitbounds='locations', visible=False)

    return templates.TemplateResponse(       # templates = Jinja2Templates(directory="src/visualization/templates/")
        "map.html",
        {
            "request": request,
            "map_html": fig.to_html()
        }
    )

@app.get("/map_direct_payment")
async def map_direct_payment(request: Request):
    with urlopen(
            'https://raw.githubusercontent.com/davidlararamos/mexico_geojson/master/latin_america.json') as response:
        latin_america = json.load(response)

    for feature in latin_america['features']:  # we are creating new keys for our dictionary
        feature['id'] = feature['properties']['sov_a3']

    lst = ['MEX', 'CHL', 'GTM', 'PER','SLV']
    lst2 = ['0.41', '1', '0.5','0.23', '0']

    df_latin_america = pd.DataFrame(list(zip(lst, lst2)),
                                    columns=['id', 'Normalized value'])
    df_latin_america['Normalized value'] = df_latin_america['Normalized value'].astype(float)

    fig = px.choropleth(df_latin_america, geojson=latin_america, locations=df_latin_america['id'],
                        color='Normalized value',color_continuous_scale="Viridis")
    fig.update_geos(fitbounds='locations', visible=False)

    return templates.TemplateResponse(       # templates = Jinja2Templates(directory="src/visualization/templates/")
        "map.html",
        {
            "request": request,
            "map_html": fig.to_html()
        }
    )

@app.get("/map_credit")
async def map_credit(request: Request):
    with urlopen(
            'https://raw.githubusercontent.com/davidlararamos/mexico_geojson/master/latin_america.json') as response:
        latin_america = json.load(response)

    for feature in latin_america['features']:  # we are creating new keys for our dictionary
        feature['id'] = feature['properties']['sov_a3']

    lst = ['MEX', 'CHL', 'GTM', 'PER','SLV']
    lst2 = ['1', '0.53', '0.66','0.46', '0']

    df_latin_america = pd.DataFrame(list(zip(lst, lst2)),
                                    columns=['id', 'Normalized value'])
    df_latin_america['Normalized value'] = df_latin_america['Normalized value'].astype(float)

    fig = px.choropleth(df_latin_america, geojson=latin_america, locations=df_latin_america['id'],
                        color='Normalized value',color_continuous_scale="Viridis")
    fig.update_geos(fitbounds='locations', visible=False)

    return templates.TemplateResponse(       # templates = Jinja2Templates(directory="src/visualization/templates/")
        "map.html",
        {
            "request": request,
            "map_html": fig.to_html()
        }
    )


@app.get("/scraping")
async def scraping(request: Request):
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
    return templates.TemplateResponse(
        "scraping.html",
        {
            "request": request,
            "timeline_plot_html": fig.to_html(),
            "n_countries": 3,
            "n_documents": 12285
        }
    )

