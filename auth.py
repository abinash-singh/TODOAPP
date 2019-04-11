
from flask import Flask, jsonify, request, make_response, session
import jwt
import datetime
from functools import wraps
from pymongo import MongoClient
import json
from simplecrypt import encrypt, decrypt

client = MongoClient("mongodb+srv://abinash-singh:gayatree%40123@cluster0-t2gln.mongodb.net/test?retryWrites=true")
mongo = client.restdb


app = Flask(__name__)
app.config['SECRET_KEY'] = 'top secret!'

def token_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        token = request.args.get('token')

        if not token:
            return jsonify({'message': 'Token is missing'})

        try:
            data = jwt.decode(token, app.config['SECRET_KEY'])
        except:
            return jsonify({'message': 'Token is invalid'})

        return f(*args, **kwargs)
    return decorated


def get_logged_user():
    if session['user_id']:
        print(session['user_id'])
        return session['user_id']
    else:
        return None


@app.route('/register/', methods=['POST'])
def register():
    user = mongo.User
    print (request)
    data = json.loads(request.data)
    user_id = user.insert_one(data)
    return jsonify({'message': 'Data saved sucessfully.'})



@app.route('/login/',  methods=['POST'])
def login():
    User = mongo.User
    print (request)
    message = 'this is a secret message'
    data = json.loads(request.data)
    if not data.get('username'):
        return jsonify({"Error": "Please provide username"})
    if not data.get('password'):
        return jsonify({"Error": "Please provide password"})

    username = data.get('username')
    password = data.get('password')
    print(username)
    message = 'this is a secret message'
    logged_user =  User.find_one({'email' : username})

    if logged_user:
        if logged_user['password'] == password:
            
            session['user_id'] = logged_user['email']
            
            token = jwt.encode({'user': username, 'exp': datetime.datetime.utcnow() + datetime.timedelta(minutes = 30)}, app.config['SECRET_KEY'])
            return jsonify({"Success": 1, "token": token.decode('UTF-8')})
        else:
            return jsonify({"Error": "Invalid Credentials"})
    else:
        return jsonify({"Error": "No user found"})
    

@app.route('/add/', methods=['POST'])
@token_required
def add():
    post_tb = mongo.Post
    print (request.data)
    logged_user_id = get_logged_user()
    data = json.loads(request.data)
    data['user_id'] = logged_user_id
    print(data)
    post_obj = post_tb.insert_one(data)
    return jsonify({'message': 'Data saved sucessfully.'})



@app.route('/dashboard/', methods=['GET'])
#@token_required
def dashboard():
    post_tb = mongo.Post
    user_tb = mongo.User
    logged_user_id = get_logged_user()

    post_data =  post_tb.find_one({'user_id' : 'megha@gmail.com'})

    post_data_list = []

    for data in post_data:
        post_data_list.append({post_data['name'], post_data['location']})

    print(post_data_list)
    #post_data_lists = json.dumps(post_data_list)
    return jsonify(post_data_list)

if __name__ == '__main__':
   app.run(debug=True, host='0.0.0.0', port=8000)

