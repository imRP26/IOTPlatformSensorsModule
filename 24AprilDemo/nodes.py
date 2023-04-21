from config import db
from flask import abort, make_response
from models import Node, nodes_schema, node_schema


def read_all():
    nodes = Node.query.all()
    return nodes_schema.dump(nodes)


def create(node):
    nodename = node.get("nodename")
    existing_node = Node.query.filter(Node.nodename == nodename).one_or_none()
    if existing_node is None:
        new_node = node_schema.load(node, session=db.session)
        db.session.add(new_node)
        db.session.commit()
        return node_schema.dump(new_node), 201
    else:
        abort(406, f"Node with nodename {nodename} already exists")


def read_one(nodename):
    node = Node.query.filter(Node.nodename == nodename).one_or_none()
    if node is not None:
        return node_schema.dump(node)
    else:
        abort(404, f"Node with nodename {nodename} not found")


def update(nodename, node):
    existing_node = Node.query.filter(Node.nodename == nodename).one_or_none()
    if existing_node:
        update_node = node_schema.load(node, session=db.session)
        existing_node.nodelatitude = update_node.nodelatitude
        existing_node.nodelongitude = update_node.nodelongitude
        existing_node.nodeip = update_node.nodeip
        existing_node.nodeport = update_node.nodeport
        existing_node.nodeactive = update_node.nodeactive
        db.session.merge(existing_node)
        db.session.commit()
        return node_schema.dump(existing_node), 201
    else:
        abort(404, f"Node with nodename {nodename} not found")


def delete(nodename):
    existing_node = Node.query.filter(Node.nodename == nodename).one_or_none()
    if existing_node:
        db.session.delete(existing_node)
        db.session.commit()
        return make_response(f"{nodename} successfully deleted", 200)
    else:
        abort(404, f"Node with nodename {nodename} not found")
