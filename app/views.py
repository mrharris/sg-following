import re
from datetime import datetime
import json

from flask import Flask, render_template, request
import shotgun_api3

from . import app

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/about/")
def about():
    return render_template("about.html")

@app.route("/contact/")
def contact():
    return render_template("contact.html")

@app.route("/hello/")
@app.route("/hello/<name>")
def hello_there(name=None):
    return render_template(
        "hello_there.html",
        name=name,
        date=datetime.now()
    )

@app.route("/api/data")
def get_data():
    return app.send_static_file("data.json")


@app.route("/following/", methods=['POST'])
def following():
    sg = shotgun_api3.Shotgun(
        "https://xxx.shotgunstudio.com",
        script_name="xxx",
        api_key="xxx",
    )

    post_dict = request.form.to_dict()
    
    entity_ids = post_dict["selected_ids"] or post_dict["ids"]
    entity_ids = [int(id_) for id_ in entity_ids.split(",")]


    user_id_to_entities = {}
    user_entities = sg.find("HumanUser", [["id", "in", entity_ids]], ["login"])
    for user_entity in user_entities:
        followed = sg.following(
            user=user_entity,
            entity_type="Task",
        )
        followed = sg.find(
                "Task",
                [["id", "in", [e["id"] for e in followed]]],
                ["content", "entity", "image"]
            )
        user_id_to_entities[user_entity["login"]] = followed


    html = _html_header()
    for user, followed in user_id_to_entities.items():
        html += "<h3>{}</h3>".format(user)
        for entity in followed:
            if entity["image"]:
                link = "https://{}/detail/{}/{}".format(
                    post_dict["server_hostname"],
                    entity["type"],
                    entity["id"],
                )
                title = "{}/{}".format(entity["entity"]["name"], entity["content"])
                html += _image_html(link, entity["image"], title)
    
    return html

def _html_header():
    return """
<html>
    <head>
        <style>
            div.gallery {
                margin: 5px;
                border: 1px solid #ccc;
                float: left;
            }
            div.desc {
                padding: 15px;
                text-align: center;
            }
        </style>
        <link rel="stylesheet" href="https://stackpath.bootstrapcdn.com/bootstrap/4.3.1/css/bootstrap.min.css" integrity="sha384-ggOyR0iXCbMQv3Xipma34MD+dH/1fQ784/j6cY/iJTQUOhcWr7x9JvoRxT2MZw1T" crossorigin="anonymous">
    </head>
    <body>
        <br>
        <h1>Followed Tasks</h1>
        <hr>
    </body>
</html>
"""

def _image_html(link, image, title):
    return """
<div class="gallery">
    <a href="{link}">
        <img src="{image}">
    </a>
    <div class="desc">{title}</div>
</div>
    """.format(link=link, image=image, title=title)