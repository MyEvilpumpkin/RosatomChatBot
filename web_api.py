from flask import render_template, request, redirect, url_for
from flask_login import login_user, logout_user, login_required, current_user
from chatbot_api import chatbot_response
from models import Users
from __init__ import create_app

app = create_app()


def reformat_response(data):
    text = str(data[0])
    index = 0
    while True:
        start_index = text.find("<img", index)
        if start_index == -1:
            break
        else:
            end_index = text.find(">", start_index)
            if end_index != -1:
                text = text.replace(text[start_index:end_index + 1], "<a onclick=\"imgOnClick(this)\">" +
                                    text[start_index:end_index + 1] + "</a>", 1)
                index = end_index
    text = text.replace("%salary", str(current_user.salary))

    commands = data[1]
    if len(commands):
        text += "</div><div class=\"msg-commands\">"
        for command in commands:
            text += "<div class=\"msg-command\" onClick=\"cmdOnClick(this.innerText)\">" + str(command[0]) + "</div>"

    return text


@app.route("/")
@login_required
def home():
    return render_template("chatbot.html")


@app.route("/getuserdata")
@login_required
def get_user_data():
    if current_user.photo is None:
        photo = url_for('static', filename='images/nophoto.jpg')
    else:
        photo = current_user.photo
    return '{"surname":"' + str(current_user.surname) + '",' + \
           '"name":"' + str(current_user.name) + '",' + \
           '"patronymic":"' + str(current_user.patronymic) + '",' + \
           '"department":"отдел ' + str(current_user.department) + '",' + \
           '"experience":"стаж с ' + str(current_user.experience) + '",' + \
           '"photo":"url(' + str(photo) + ')",' + \
           '"version":"Версия 0.25"}'


@app.route("/getresponse")
@login_required
def get_bot_response():
    user_text = request.args.get('msg')
    response = chatbot_response(user_text)
    return reformat_response(response)


@app.route("/getfirstmessage")
@login_required
def get_first_bot_message():
    response = chatbot_response('Привет')
    first_response = ('Привет, я - Атом, бот-помощник!<br>Я помогу тебе освоиться в нашей компании.<br>'
                      'Что ты хочешь у меня спросить?', response[1])
    return reformat_response(first_response)


@app.route('/login')
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    return render_template('login.html')


@app.route('/login', methods=['POST'])
def login_post():
    user_login = request.form.get('login')
    user_password = request.form.get('password')
    user = Users.query.filter_by(login=user_login, password=user_password).first()
    if not user:
        return redirect(url_for('login', em=True))
    login_user(user, remember=True)
    return redirect(url_for('home'))


@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))


@app.route('/getquests')
@login_required
def get_quests():
    return "<div>test quests</div>"


if __name__ == "__main__":
    app.run()
