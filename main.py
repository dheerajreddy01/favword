
from sqlalchemy import ForeignKey,UniqueConstraint
from flask import Flask,request,jsonify
from flask_sqlalchemy import SQLAlchemy 
from flask_cors import CORS,cross_origin
from sqlalchemy import true
from werkzeug.security import generate_password_hash, check_password_hash

from sqlalchemy.exc import IntegrityError





app = Flask(__name__)
# mail = Mail(app)
cors = CORS(app)
app.config['SECRET_KEY'] = '!9m@S-dThyIlW[pHQbN^'
app.config['CORS_HEADERS'] = 'Content-Type'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///word.db'







db = SQLAlchemy(app)

class User(db.Model):

    _tablename_ = 'usertable'
    id = db.Column(db.Integer, primary_key=True)
    name= db.Column(db.String(15))
    username = db.Column(db.String(30))
    email = db.Column(db.String(50), unique=True)
    password = db.Column(db.String(256), unique=True)
    

    def __init__(self,name,username,email,password):
        self.name = name
        self.username=username
        self.email=email
        self.password=password


    def serialize(self):
        return {
            "id": self.id,
            "name": self.name,
            "username":self.username,
            "email":self.email
            }


class Word(db.Model):
        id = db.Column(db.Integer, primary_key=True)
        sentence= db.Column(db.String(100),unique=True)

        def __init__(self,sentence):
            self.sentence=sentence

        def serialize(self):
            return{
                "id":self.id,
                "sentence":self.sentence
            }

 
 











class Order(db.Model):
    _tablename_="order"
    id=db.Column(db.Integer,primary_key=True)
    user_id=db.Column(db.Integer)
    word_id=db.Column(db.Integer,ForeignKey('word.id')) 
    word=db.Column(db.String(100))
    db.UniqueConstraint(user_id,word_id)

    # def __init__(self,sentence,user_id,word_id):
    #     self.sentence = sentence
    #     # self.email = email
    #     self.user_id = user_id
    #     self.word_id =  word_id

    def serialize(self):
        return{
            "id":self.id,
            "sentence":self.word,
            "user_id":self.user_id,
            "word_id":self.word_id
        }

 

@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"
# def mail():
#      msg = message("hello", sender="chsanavi@gmail.com", recipients=["chsanavi@gmail.com"])
#      mail.send(msg)
#      return "message sent!"

@app.route('/register', methods = ['POST'])
@cross_origin()
def register():

    if request.method == 'POST' :
        hashed_password = generate_password_hash(request.json['password'], method='sha256')
        new_user = User(
            name = request.json['name'], 
            username = request.json['username'] ,
            email = request.json['email'] ,
            password = hashed_password )
            # message = request.json['you have subscribed my email'],
            # server = smtplib.SMTP("smtp.gmail.com", 587)
            # server.starttls()
            # server.login("chsanavi@mail.com")
            # server.sendmail({"email"})

        try:
            db.session.add(new_user)
            db.session.commit()
            return jsonify({'user': new_user.serialize()}), 201
        except:
             return jsonify({"status": 400,
                        "message": "Failure to add user details.This may occur due to duplicate entry of userdetails"})


@app.route('/login', methods = ['POST'])
@cross_origin()
def login():
    if request.method == 'POST' :
        
        user = User.query.filter_by(email = request.json['email']).first()
        if user:
             
            if check_password_hash(user.password, request.json['password']):
               
               
                return jsonify({'user': user.serialize(),'message':"login Successful"}), 200
            else:
                return jsonify({"message": "user password wrong", "status": 400}),400
        else:
            return jsonify({"message": "user details doesnt exist", "status": 400}),400


@app.route("/word",methods=['POST','GET'])
def word():
    if(request.method=='GET'):
        return jsonify({'Word': list(map(lambda word: word.serialize(), Word.query.all()))})

    else:
        sentence=request.json['sentence']
        order=Word(sentence)
        db.session.add(order)
        db.session.commit()
        return jsonify({"status": 200, "message": "updated"})


@app.route("/srch/<string:word>",methods=['GET'])
def srch(word):
    return jsonify({'Word': list(map(lambda word: word.serialize(), Word.query.filter(Word.sentence.contains(word))))})






@app.route("/subs",methods=["POST","GET"])
def subs():
    if(request.method=="GET"):
         return jsonify({'Order': list(map(lambda word: word.serialize(), Order.query.all()))})


    else:   
        sentence=request.json['sentence']
        email=request.json['email']
        uid=request.json['user_id']
        wd=request.json['word_id']  
        subs=Order(sentence=sentence, email=email, user_id=uid, word_id=wd)
        db.session.add(subs)
        db.session.commit()
        return jsonify({"status": 200, "message": "updated"})



# @app.route("/email")
# def mail():
#      msg = message("hello", sender="samyu.2k1@gmail.com", recipients=["samyu.2k1@gmail.com"])
#      mail.send(msg)
#      return 'message sent!'

@app.route('/subscribe',methods=['POST'])
@cross_origin()
def addsubscribe():
    user_id=request.json['user_id']
    word_id=request.json['word_id']
    # word=request.json['word']
    word_db=Word.query.get(word_id)
    if word_db is None:
        return jsonify({"status":404,"message":"word not found, send a valid word_id"})
    word=word_db.sentence
    subscribe=Order(user_id=user_id,word_id=word_id,word=word)
    try:
        db.session.add(subscribe)
        db.session.commit()
    except IntegrityError as ie:
        print(ie)
        return jsonify({"status":400,"message":str(ie)}) 
    return jsonify({"status":200,"message":"subscribed successfully"})
    
@app.route('/subscribe/<int:user_id>',methods=['GET'])
@cross_origin()
def getsubscribe(user_id):
 return jsonify({'Order': list(map(lambda order: order.serialize(), Order.query.filter(Order.user_id==user_id)))})


@app.route("/unsubscribe/<int:id>", methods=["DELETE"])
def guide_delete(id):
    # response = {} setting a variable named response to an empty dictionary to take in full todos.
    response = {}
    unscubscribe= Order.query.get(id)
    # response['id'] = todo.id sets the response id to the todo.id
    response['id'] = unscubscribe.id
    print(unscubscribe)
    db.session.delete(unscubscribe)
    # db.session.delete(todo) calls SQL DELETE statement onto the database and deletes the todo that matches the same ID
    db.session.commit()

    return jsonify({"status":201,"message":"unsubscribed successfully"})


# @app.route('/gmails', methods = ['POST'])
# @cross_origin()
# def getmails():
#    try:
#     mailchimp = MailchimpTransactional.Client("hKOU8XUutP7oLoJ_KL2tAA")
#     response = mailchimp.messages.send({"message": {}})
#         print (response)
#     except ApiClientError as error:
#        print ("An exception occurred: {}".format(error.text))



# @app.route("/gmails", methods=['GET'])
# @cross_origin()
# def gmails():
#    try:
#        mailchimp = MailchimpTransactional.Client("hKOU8XUutP7oLoJ_KL2tAA")
#        response = mailchimp.messages.send({"message": {"text":"Hi Sanavi","subject":"Test Mail","from_email":"chsanavi@gmail.com","to":'["email":"chsanavi@gmail.com"]'}})
#        return jsonify({"status":200,"message":response})
#    except ApiClientError as error:
#        return ("An exception occurred: {}".format(error.text))


if __name__=="__main__":
    db.create_all()
    app.run(debug=True, port=8000)
    

