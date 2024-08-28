import flask

app = flask.Flask(__name__, template_folder="./templates", static_folder="./static")

@app.route("/play")
def play():
    name = flask.request.args.get("name")
    if name == None:
        return flask.Response("Cannot Get key 'name'", 400)
    return flask.render_template("main.html",name=name)
    
app.run(debug=True,port=8000,host="0.0.0.0")