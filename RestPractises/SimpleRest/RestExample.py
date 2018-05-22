from flask import Flask,jsonify,request,Request,render_template
# from flask_pymongo import  PyMongo
from pymongo import MongoClient
import json

app = Flask(__name__)

'''for flask pymongo'''
# app.config['MONGO_DBNAME'] = 'songs'
# app.config['MONGO_URI'] = 'mongodb://admin:admin@localhost:27017/songs'
#
#
# mongo = PyMongo(app)

'''for general'''
mongo = MongoClient('localhost',27017)
table = mongo.songs.top_songs;
songs = list(table.find(projection={'_id':0}))


@app.route('/',methods=['GET'])
def index():
    return render_template('index.html',songs=songs)
    # return jsonify({'message':'hello world'})


@app.route('/songs/',methods=['GET'])
@app.route('/songs',methods=['GET'])
def get_all_names():
    return jsonify({'songs':songs})


@app.route('/songs/<song>',methods=['GET'])
def get_particular_name(song):
    cur_song = [cur for cur in songs if str(cur['name']).replace(' ','').lower() == str(song).replace('+','').lower()]
    if cur_song:
        return jsonify({'song':cur_song})
    else:
        return jsonify({'message':'invalid!!'})


@app.route('/songs/',methods=['POST'])
@app.route('/songs',methods=['POST'])
def set_data():
    cur_song = {'name':request.json['name'],'artist':request.json['artist'],'genre':request.json['genre']}
    for song in songs:
        if str(song['name']).replace(' ','').lower() == str(cur_song['name']).replace(' ','').lower():
            return jsonify({'message':'failure !!!!'})
    table.insert_one(cur_song)
    songs.append(cur_song)
    return jsonify({'message':'success'})


@app.route('/songs/<song>',methods=['PUT'])
def modify_data(song):
    cur_song = [record for record in songs if str(record['name']).replace(' ','').lower() == str(song.replace('+','')).lower()]
    if not cur_song:
        return jsonify({'message':'invalid!!'})
    updated = [{'name':'','artist':'','genre':''}]
    updated[0]['name'] = request.json['name'] if request.json['name'] else cur_song[0]['name']
    updated[0]['artist'] = request.json['artist'] if request.json['artist'] else cur_song[0]['artist']
    updated[0]['genre'] = request.json['genre'] if request.json['genre'] else cur_song[0]['genre']
    table.update_one({'name':cur_song[0]['name'],'artist':cur_song[0]['artist'],'genre':cur_song[0]['genre']},
                     {'$set':{'name':updated[0]['name'],
                              'artist':updated[0]['artist'],
                              'genre':updated[0]['genre']},
                      },
                     upsert=False)
    songs[int(songs.index(cur_song[0]))] = updated[0]
    return jsonify({'song':updated[0]})


@app.route('/songs/<song>',methods=['DELETE'])
def delete_data(song):
    cur_name = [name_in for name_in in songs if str(name_in['name']).replace(' ','').lower() == str(song).replace('+','').lower()]
    if not cur_name:
        return jsonify({'message':'invalid!!'})
    songs.remove(cur_name[0])
    table.delete_one({'name':cur_name[0]['name'],'artist':cur_name[0]['artist'],'genre':cur_name[0]['genre']})
    return jsonify({'deleted':cur_name[0]})


if __name__ == '__main__':
    app.config['JSONIFY_PRETTYPRINT_REGULAR ']=True
    app.run('localhost',5151,debug=True)