import csv, json, math

class Team:
    def __init__(self, name, uid):
        self.name = name
        self.uid = uid
        self.level = 0
        self.stats = {}

class Helper:
    def __init__(self):
        pass
        
    def numberize(self, text):
        try:
            return int(text)
        except:
            return 0

    def readit(self, file_path):
        f = open(file_path, encoding = 'utf-8')
        r = csv.reader(f, delimiter=';')
        lines = []
        for line in r:
            lines.append(line)
        lines = lines[1:]
        return lines

    def getteamsdata(self, lines):
        teams = {}
        for line in lines:
            if len(line) == 2:
                name = line[0].replace(" ", "").lower()
                uid = line[1].replace(" ", "").lower()
                team = Team(name, uid)
                teams[uid] = team
        return teams

    def gethintdata(self, lines, speed):
        stages = {}
        for line in lines:
            stage_id = self.numberize(line[0])
            code = line[1].replace(" ", "").lower()
            hints = []
            for i in range(2, len(line)-1):
                if i%2 == 0:
                    hint_text = line[i]
                    hint_time = self.numberize(line[i+1])
                    hint_time = math.ceil(hint_time / speed)
                    hint = {"text": hint_text, "time": hint_time}
                    if hint["text"] != "":
                        hints.append(hint)
            if stage_id != 0:
                stages[str(stage_id)] = {"code": code, "hints": hints}
        return stages
    
    def gettransdata(self, lines):
        if len(lines) == 0:
            return {}
        t = {}
        header = lines.pop(0)
        langs = header[1:]
        for line in lines:
            if len(line) == len(langs)+1:
                definition = line.pop(0)
                translations = {}
                for i in range(len(langs)):
                    lang = langs[i]
                    trans = line[i]
                    translations[lang] = trans
                t[definition] = translations
        return t
    
    def loaddata(self):
        config = json.load(open("./data/config.json", encoding="utf-8"))
        stages = self.gethintdata(self.readit("./data/hints.csv"), config['speed'])
        teams = self.getteamsdata(self.readit("./data/teams.csv"))
        uids = list(teams.keys())
        admcode = config['admcode']
        lang = config['lang']
        trans = self.gettransdata(self.readit("./data/trans.csv"))
        vars = [stages, teams, uids, admcode, lang, trans]
        return {
            'config': config,
            'stages': stages,
            'teams': teams,
            'uids': uids,
            'admcode': admcode,
            'lang': lang,
            'trans': trans
        }