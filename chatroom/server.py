import flask as f
import flask_socketio as fsio
import random
from string import ascii_letters

app= f.Flask(__name__)
app.config["SECRET_KEY"]="hgddfgds"
app.config["DEBUG"]=True
socketio=fsio.SocketIO(app)
rooms={}
def rommcodegen(l):
    s=''.join(random.choice(ascii_letters) for i in range(l))
    return s

@app.route("/", methods=["POST","GET"])
def home():
    f.session.clear()
    if f.request.method== "POST":
        name=f.request.form.get("name")
        code=f.request.form.get("code")
        join=f.request.form.get("join room",False)
        create=f.request.form.get("create room",False)
        if not name:
            return f.render_template("homepg.html", error="Enter name please",code=code,name=name)
        #rcode=code
        if join != False and not code:
            return f.render_template("homepg.html", error="Enter room code please",code=code,name=name)
        temp=rommcodegen(4)
        room=code

        if create != False:
            room=temp
            rooms[room]={"members":0,"messages":[]}
        elif code not in rooms:
            return f.render_template("homepg.html", error="Room does not exist" ,code=code,name=name)
        
        f.session["room"]= room
        f.session["name"]=name
        return f.redirect(f.url_for("room"))
    
    return f.render_template("homepg.html")
@app.route("/room")
def room():
    room = f.session.get("room")
    if room is None or f.session.get("name") is None or room not in rooms:
        return f.redirect(f.url_for("home"))
    return f.render_template("chtroom.html",code=room,messages=rooms[room]["messages"])

@socketio.on("message")
def message(data):
    room = f.session.get("room")
    if room not in rooms:
        return 
    
    content = {
        "name": f.session.get("name"),
        "message": data["data"]
    }
    fsio.send(content, to=room)
    rooms[room]["messages"].append(content)
    print(f"{f.session.get('name')} said: {data['data']}")

@socketio.on("connect")
def connect():
    room=f.session.get("room")
    name=f.session.get("name")
    if room not in rooms:
        fsio.leave_room(room)
        return
    
    fsio.join_room(room)
    fsio.send({"name": name, "message": "has joined the party"}, to=room)
    rooms[room]["members"] += 1
    print(f"{name} joined room {room}")
@socketio.on("disconnect")
def disconnect():
    room = f.session.get("room")
    name = f.session.get("name")
    fsio.leave_room(room)

    if room in rooms:
        rooms[room]["members"] -= 1
        if rooms[room]["members"] <= 0:
            del rooms[room]
    
    fsio.send({"name": name, "message": "has left the room"}, to=room)


if __name__=="__main__":
    socketio.run(app,host="localhost")


                       


