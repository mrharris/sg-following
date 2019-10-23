import re
from datetime import datetime
import json
import os

from flask import Flask, render_template, request, jsonify, url_for
import shotgun_api3

from . import app

# TODO
# unfollow button
# unfollow selected button

sg = shotgun_api3.Shotgun(
    os.environ.get("SG_URL"),
    script_name=os.environ.get("SG_SCRIPT_NAME"),
    api_key=os.environ.get("SG_SCRIPT_KEY"),
)


@app.route("/following", methods=["POST"])
def following():
    post_dict = request.form.to_dict()
    entity_ids = post_dict["selected_ids"] or post_dict["ids"]
    entity_ids = [int(id_) for id_ in entity_ids.split(",")]
    user = sg.find_one("HumanUser", [["id", "is", entity_ids[0]]], ["name"])

    return render_template("datatables.html", user=user)


@app.route("/following/<string:entity_type>/<int:user_id>")
def followed_entities(entity_type, user_id):
    entities = get_followed_entities({"type": "HumanUser", "id": user_id}, entity_type)
    return jsonify({"data": entities})


@app.route("/unfollow", methods=["POST"])
def unfollow_entities():
    request_json = request.get_json()
    user = {"type": "HumanUser", "id": request_json["user_id"]}
    entities = request_json["entities"]
    for entity in entities:
        print("Unfollowing", entity)
        sg.unfollow(user, entity)
    return jsonify({"success": True})


def get_followed_entities(user, entity_type):

    followed = sg.following(user=user, entity_type=entity_type)

    entity_queries = {
        "Asset": ["code", "image"],
        "Shot": ["code", "image"],
        "Task": ["content", "entity", "image"],
        "Version": ["code", "entity", "image"],
        "Note": ["subject", "note_links"],
    }

    # populate the shotgun entities so they have
    # the fields we want to show in the tables
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
    entity["image"] = entity.get("image") or url_for(
        "static", filename="placeholder.png"
    )

    # recurse through any linked entities
    for field, value in entity.items():
        if not isinstance(value, list):
            value = [value]
        for v in value:
            if isinstance(v, dict) and "id" in v:
                conform(v)
