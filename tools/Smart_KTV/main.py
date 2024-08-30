import flask

app = flask.Flask(__name__, template_folder="./templates", static_folder="./static")

@app.route("/play")
def play():
    name = flask.request.args.get("name")
    disc = flask.request.args.get("disc")
    song_name = flask.request.args.get("song_name")
    singer = flask.request.args.get("singer")
    return flask.render_template("main.html",name=name,disc=disc,song_name=song_name,singer=singer)
    
app.run(debug=True,port=8000,host="0.0.0.0")