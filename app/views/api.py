# Content DB
# Copyright (C) 2018  rubenwardy
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.


from flask import *
from flask_user import *
from app import app
from app.models import *
from app.utils import is_package_page
from app.querybuilder import QueryBuilder

@app.route("/api/packages/")
def api_packages_page():
	qb    = QueryBuilder(request.args)
	query = qb.buildPackageQuery()
	ver   = qb.getMinetestVersion()

	pkgs = [package.getAsDictionaryShort(app.config["BASE_URL"], version=ver) \
			for package in query.all()]
	return jsonify(pkgs)

@app.route("/api/packages/<author>/<name>/")
@is_package_page
def api_package_page(package):
	return jsonify(package.getAsDictionary(app.config["BASE_URL"]))


@app.route("/api/topics/")
def api_topics_page():
	qb     = QueryBuilder(request.args)
	query  = qb.buildTopicQuery(show_added=True)
	return jsonify([t.getAsDictionary() for t in query.all()])


@app.route("/api/topic_discard/", methods=["POST"])
@login_required
def topic_set_discard():
	tid = request.args.get("tid")
	discard = request.args.get("discard")
	if tid is None or discard is None:
		abort(400)

	topic = ForumTopic.query.get(tid)
	if not topic.checkPerm(current_user, Permission.TOPIC_DISCARD):
		abort(403)

	topic.discarded = discard == "true"
	db.session.commit()

	return jsonify(topic.getAsDictionary())


@app.route("/api/minetest_versions/")
def api_minetest_versions_page():
	return jsonify([{ "name": rel.name, "protocol_version": rel.protocol }\
			for rel in MinetestRelease.query.all() if rel.getActual() is not None])
