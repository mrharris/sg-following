import re
from datetime import datetime
import json
import os

from flask import Flask, render_template, request, jsonify
import shotgun_api3

from . import app

# TODO
# single user
# unfollow button
# unfollow selected button
# render datatables from flask

sg = shotgun_api3.Shotgun(
    os.environ.get("SG_URL"),
    script_name=os.environ.get("SG_SCRIPT_NAME"),
    api_key=os.environ.get("SG_SCRIPT_KEY"),
)

@app.route("/")
def home():
    v = os.environ.get("SG_URL"),
    return jsonify(get_followed_entities(
        {"type": "HumanUser", "id": 101},
        {"type": "Project", "id": 137},
    ))

@app.route("/following/", methods=['POST'])
def following():
    post_dict = request.form.to_dict()

    sg_server = "https://{}".format(post_dict["server_hostname"])
    entity_ids = post_dict["selected_ids"] or post_dict["ids"]
    entity_ids = [int(id_) for id_ in entity_ids.split(",")]
    project = {"type": "Project", "id": 137}
    user_id_to_entities = {}

    sg = shotgun_api3.Shotgun(
        sg_server,
        script_name=os.environ.get("SG_SCRIPT_NAME"),
        api_key=os.environ.get("SG_SCRIPT_KEY"),
    )

    user_entities = sg.find("HumanUser", [["id", "in", entity_ids]], ["login"])
    for user in user_entities:
        entities = get_followed_entities(user, project, "Task")
        user_id_to_entities[user["login"]] = entities

    return jsonify(entities)


@app.route("/following/task")
def following_task():
    entities = get_followed_entities(
        {"type": "HumanUser", "id": 101},
        {"type": "Project", "id": 137},
        "Task",
    )
    return jsonify({"data": entities})

@app.route("/following/note")
def following_note():
    entities = get_followed_entities(
        {"type": "HumanUser", "id": 101},
        {"type": "Project", "id": 137},
        "Note",
    )
    return jsonify({"data": entities})


def get_followed_entities(user, project, entity_type):

    followed = sg.following(user=user, project=project, entity_type=entity_type)

    entity_queries = {
        "Asset": ["code", "image"],
        "Shot": ["code", "image"],
        "Task": ["content", "entity", "image"],
        "Version": ["code", "entity", "image"],
        "Note": ["subject", "note_links"],
    }

    # populate the shotgun entities
    entities = [e for e in followed if e["type"] == entity_type]
    if entities:
        entities = sg.find(
                entity_type,
                [["id", "in", [e["id"] for e in entities]]],
                entity_queries[entity_type],
            )
        for entity in entities:
            conform(entity)
    return entities

def entity_url(entity):
    return "{}/detail/{}/{}".format(sg.base_url, entity["type"], entity["id"])

def conform(entity):
    """Ensure this entity has the fields needed by datatables"""
    entity["url"] = entity_url(entity)
    entity["image"] = entity.get("image") or "placeholder.png"
    
    # recurse through any linked entities
    for field, value in entity.items():
        if not isinstance(value, list):
            value = [value]
        for v in value:
            if isinstance(v, dict) and "id" in v:
                conform(v)