from flask import Flask, render_template, request, g
from waitress import serve
import time, os
import csv, json, math
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

def format(text):
    text = text.replace(" ", "").lower()
    return text

def gettimeobj():
    zone = ZoneInfo("Europe/Prague")
    timeobj = datetime.now(zone)
    return timeobj

def tabletostring(headerline, lines):
    content = ''
    th = ''
    for elem in headerline:
        th += f'<th>{elem}</th>'
    content += f'<tr>{th}</tr>'    
    for row in lines:
        tr = ''
        for elem in row:
            tr += f'<td>{elem}</td>'
        content += f'<tr>{tr}</tr>'
    return f'<table id="restable">{content}</table>'

def numberize(text):
    try:
        return int(text)
    except:
        return 0

def readit(file_path):
    f = open(file_path, encoding = 'utf-8')
    r = csv.reader(f, delimiter=';')
    lines = []
    for line in r:
        lines.append(line)
    lines = lines[1:]
    return lines

def getteamsdata(lines):
    teams = {}
    for line in lines:
        if len(line) == 2:
            name = format(line[0])
            uid = format(line[1])
            team = Team(name, uid)
            teams[uid] = team
    return teams

def gethintdata(lines, speed):
    stages = {}
    for line in lines:
        stage_id = numberize(line[0])
        code = format(line[1])
        hints = []
        for i in range(2, len(line)-1):
            if i%2 == 0:
                hint_text = line[i]
                hint_time = numberize(line[i+1])
                hint_time = math.ceil(hint_time / speed)
                hint = {"text": hint_text, "time": hint_time}
                if hint["text"] != "":
                    hints.append(hint)
        if stage_id != 0:
            stages[str(stage_id)] = {"code": code, "hints": hints}
    return stages

class Team():
    def __init__(self, name, uid):
        self.name = name
        self.uid = uid
        self.level = 0
        self.stats = {}

class GlobalVariables():
    def __init__(self):
        self.config = json.load(open("./data/config.json", encoding="utf-8"))
        self.teams = getteamsdata(readit("./data/teams.csv"))
        self.uids = list(self.teams.keys())
        self.stages = gethintdata(readit("./data/hints.csv"), self.config['speed'])
        self.admcode = 'bidlo42'       

gv = GlobalVariables()

def gettn(uid):
    return gv.teams[uid].name


def get_hint_string(uid):
    try:
        level = gv.teams[uid].level
        stringlevel = str(level)
        timeonlevel = gv.teams[uid].stats[stringlevel]
        timenow = gettimeobj()
        timewait = (timenow - timeonlevel).total_seconds()

        #how many hints should they get
        hints = gv.stages[stringlevel]["hints"]
        hintstext = ""

        if len(hints) < 1:
            return ("Nápovědy nejsou zatím k dispozici. Zadej kód stanoviště.", False)

        for i in range (len(hints)):
            if timewait > hints[i]['time']:
                timewait -= hints[i]['time']
                hinttext = hints[i]['text']
                hintstext += f"{i+1}. nápověda: \n {hinttext} \n \n"
            else:
                missingtime = hints[i]['time'] - timewait
                nexthinttime = timenow + timedelta(seconds=missingtime)
                stringtime = nexthinttime.strftime("%H:%M:%S")
                hintstext += f"{i+1}. nápověda: \n Dostaneš ji v {stringtime}"
                break
        return (hintstext, True)
    except:
        return ("Nápovědy nejsou zatím k dispozici. Zadej kód stanoviště", False)

app = Flask(__name__)
@app.route('/')
@app.route('/index')
def get_login_page():
    return render_template('index.html', msg='', msgcolor='neut')

@app.route('/getconfig')
def get_config():
    return gv.config

@app.route('/main')
def get_main_page():
    uid = format(request.args.get('tname'))
    if uid == gv.admcode:
        return render_template('admin.html', msg='Info: Přihlášení do admin menu.', msgcolor='pos')
    elif uid in gv.uids:
        return render_template('main.html', msg='Přihlášení bylo úspěšné.', msgcolor='pos', tn=gettn(uid))   
    else:
        return render_template('index.html', msg='Přihlašovací kód neexistuje.', msgcolor='neg')

@app.route('/entered')
def entered():
    code = format(request.args.get('code'))
    uid = format(request.args.get('tname'))
    if uid in gv.uids:
        for stageid in gv.stages.keys():
            stage = gv.stages[stageid]
            stagecode = stage['code']
            if code == stagecode:
                levelid = int(stageid)
                lastlevelid = gv.teams[uid].level
                if levelid < 0 and levelid == lastlevelid or levelid > 0 and stageid in gv.teams[uid].stats.keys():
                    return render_template('main.html', msg='Tento kód jste již zadali', msgcolor='neg', tn=gettn(uid))
                else:
                    gv.teams[uid].level = levelid
                    gv.teams[uid].stats[stageid] = gettimeobj()
                    (hintstring, status) = get_hint_string(uid)
                    color = 'neg'
                    if status: color = 'pos'
                    return render_template('main.html', msg='Úspěch! \n \n' + hintstring, msgcolor=color, tn=gettn(uid))
        return render_template("main.html", msg="Špatný kód stanoviště.", msgcolor='neg', tn=gettn(uid))
    else:
        return render_template("main.html", msg="Tým nenalezen.", msgcolor='neg', tn="")

@app.route('/get-hint')
def get_hint():
    try:    
        uid = format(request.args.get('tname'))
        (hintstring, status) = get_hint_string(uid)
        color = 'neg'
        if status: color = 'neut'
        return {
            'msg': f'\n \n {hintstring}',
            'suc': color
        }
    except:
        try:
            uid = format(request.args.get('tname'))
            return {'msg': '', 'suc': 'neut'}
        except:
            return {'msg': 'Tým neexistuje.', 'suc': 'neg'}

@app.route('/get-stats')
def get_stats():
    adminid = format(request.args.get('tname'))
    if adminid == gv.admcode:
        header = '<h2 id="tableheader">Výsledky: \n </h2>'
        firstline = ['Název týmu']
        for stageid in gv.stages.keys():
            if int(stageid) > 0:
                firstline.append(stageid)
        lines = []
        for uid in gv.teams.keys():
            name = gv.teams[uid].name
            line = [name]
            for key in firstline[1:]:
                if key in gv.teams[uid].stats.keys():
                    timestring = gv.teams[uid].stats[key].strftime("%H:%M:%S")
                    line.append(timestring)
                else:
                    line.append('-')
            lines.append(line)
        stringtable = tabletostring(firstline, lines)
        return render_template('admin.html', msg=header + stringtable, msgcolor='neut')          
    else:
        return render_template('index.html', msg='Nejsi admin, táhni!', msgcolor = 'neg')

@app.route('/reset-game')
def reset_game():
    uid = format(request.args.get('tname'))
    if uid == gv.admcode:
        resetuid = format(request.args.get('rname'))
        if resetuid in gv.uids:
            gv.teams[resetuid].stats = {}
            gv.teams[resetuid].level = 0
            return render_template('admin.html', msg=f'Info: Tým {gv.teams[resetuid].name} obnoven.', msgcolor='pos')
        else:
            return render_template('admin.html', msg=f'Info: Tým nenalezen.', msgcolor='neg')
    else:
        return render_template('index.html', msg='Nejsi admin, táhni!', msgcolor = 'neg')

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    serve(app, host="0.0.0.0", port=port)