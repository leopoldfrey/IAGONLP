import sys
from stanfordnlp.server import CoreNLPClient
from pyosc import Server
from pyosc import Client
from threading import Thread

class DownThread(Thread):
    def __init__(self, textinput, osc_client, option, nlp_server):
        Thread.__init__(self)
        self.textinput = textinput
        self.osc_client = osc_client
        self.option = option
        self.nlp_server = nlp_server
        
    def run(self):
        print("--> INPUT :", self.textinput)
        
        nlp = self.nlp_server
        # submit the request to the server
        ann = nlp.annotate(self.textinput)
        
        if(self.option == 'part_of_speech'):
            print("----> PART OF SPEECH : ", self.textinput)
            done = False
            grp = ""
            for xs in range(len(ann.sentence)):
                for xt in range(len(ann.sentence[xs].token)):
                    t = ann.sentence[xs].token[xt]
                    self.osc_client.send('/token/'+t.pos, t.word)
                
                    if (t.pos == "NOUN" or t.pos == "PROPN"):
                        #print("NOUN ", t.word)
                        if(grp == ""):
                            grp = t.word
                        else:
                            grp += " " + t.word
                        done = False
                    elif (t.pos == "ADJ"):
                        #print("ADJ ", t.word)
                        if(grp == ""):
                            grp = t.word
                        else:
                            grp += " " + t.word
                        done = False
                    #elif (t.pos == "ADV" or t.pos == "CONJ"):   
                    #    if(grp != ""):
                    #        grp += " " + t.word
                    #    done = False
                    else:
                        if(grp != ""):
                            print("- NOMINAL GROUP "+grp)
                            self.osc_client.send('/grp', grp)
                            done = True
                        grp = ""
                        #print "OTHER type : " + pos[x][1] + " word : " + pos[x][0]
                if (not done and grp != ""):
                    print("- NOMINAL GROUP "+grp)
                    self.osc_client.send('/grp', grp)
        
        elif(self.option == 'named_entities'):
            print("----> NAMED ENTITIES : " + self.textinput)
            #print 'Named Entities:', nlp.ner(message)
            for xs in range(len(ann.sentence)):
                for xt in range(len(ann.sentence[xs].token)):
                    t = ann.sentence[xs].token[xt]
                    self.osc_client.send('/entity/'+t.ner, t.word)
                
        elif(self.option == 'constituency_parsing'):
            print('----> CONSTITUENCY PARSING :')
            for xs in range(len(ann.sentence)):
                print(ann.sentence[xs].parseTree)
                
        elif(self.option == 'dependency_parsing'):
            print('----> DEPENDENCY PARSING :')
            for xs in range(len(ann.sentence)):
                print(ann.sentence[xs].basicDependencies)
                
        elif(self.option == 'tokenize'):
            print('----> TOKENIZE :')
            for xs in range(len(ann.sentence)):
                    for xt in range(len(ann.sentence[xs].token)):
                        t = ann.sentence[xs].token[xt]
                        self.osc_client.send('/token/'+t.pos, t.word)
                        
        elif(self.option == 'lemmatize'):
            print('----> LEMMATIZE :')
            for xs in range(len(ann.sentence)):
                    for xt in range(len(ann.sentence[xs].token)):
                        t = ann.sentence[xs].token[xt]
                        print(t.word," : ", t.lemma)
                        
        elif(self.option == 'coreference'):
            print('----> COREFERENCE :')
            print(ann.corefChain)
            
        elif(self.option == 'sentiment'):
            print('----> SENTIMENT :')
            for xs in range(len(ann.sentence)):
                for xt in range(len(ann.sentence[xs].token)):
                    t = ann.sentence[xs].token[xt]
                    print(t.word, " : ", t.sentiment)
            
class StanfordNLP2:
    
    def __init__(self, osc_server_port=9920, osc_client_host='127.0.0.1', osc_client_port=9921):
        self.osc_server = Server('127.0.0.1', osc_server_port, self.callback)
        self.osc_client = Client(osc_client_host, osc_client_port)
        self.option = 'part_of_speech'
        # 'lemma','parse','depparse','coref'
        properties = {
            # segment
            "tokenize.language": "fr",
            # pos
            "pos.model": "edu/stanford/nlp/models/pos-tagger/french/french-ud.tagger",
            # parse
            "parse.mode": "edu/stanford/nlp/models/lexparser/frenchFactored.ser.gz",
            # depparse
            "depparse.model": "edu/stanford/nlp/models/parser/nndep/UD_French.gz",
            "depparse.language": "french"
        }
        self.nlp_server = CoreNLPClient(annotators=['tokenize','ssplit','pos','ner', 'sentiment'], timeout=30000, memory='4G', be_quiet=False, properties=properties)   
        self.search("Au quatrième top, le serveur sera prêt. Top, Top, Top, Top !!!")
        print("Stanford NLP2 Ready")

    def callback(self, address, *args):
        if address == '/option':
            self.option = str(args[0])
            print("-mode "+self.option)
        elif address == '/search':
            s = ""
            l = len(args)
            for x in range(0,l):
                s += str(args[x])
                if(x < (l-1)):
                    s += " "
            self.search(s)
        else:
            print("callback : "+str(address))
            for x in range(0,len(args)):
                print("     " + str(args[x]))
    
    def search(self, message):
        '''
        message = message.strip('\'')
        message = message.replace(",", " ")
        message = message.replace('à', "a")
        message = message.replace("â", "a")
        message = message.replace("é", "e")
        message = message.replace("è", "e")
        message = message.replace("ê", "e")
        message = message.replace("ë", "e")
        message = message.replace("î", "i")
        message = message.replace("ï", "i")
        message = message.replace("ô", "o")
        message = message.replace("ö", "o")
        message = message.replace("ù", "u")
        message = message.replace("ü", "u")
        message = message.replace("ç", "c")
        message = message.replace(")", " ")
        message = message.replace(", ", " ")
        message = message.replace("… ", " ")
        message = message.replace('\xe2\x80\x99', "'")
        #'''
        
        if(self.option == 'all'):
            thd = DownThread(message, self.osc_client, 'part_of_speech', self.nlp_server);
            thd.start();
            thd2 = DownThread(message, self.osc_client, 'named_entities', self.nlp_server);
            thd2.start();
        else:
            thd = DownThread(message, self.osc_client, self.option, self.nlp_server);
            thd.start();
        
if __name__ == '__main__':
    if len(sys.argv) == 1:
        StanfordNLP2();
    elif len(sys.argv) == 4:
        StanfordNLP2(int(sys.argv[1]), sys.argv[2], int(sys.argv[3]))
    else:
        print('usage: %s <osc-server-port> <osc-client-host> <osc-client-port>')