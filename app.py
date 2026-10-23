import os, json, sqlite3, urllib.request, urllib.error
from flask import Flask, request, jsonify, send_from_directory

ROOT=os.path.dirname(os.path.abspath(__file__))
DB=os.path.join(ROOT,'library.db')
app=Flask(__name__,static_folder='static')

def db():
    c=sqlite3.connect(DB)
    c.row_factory=sqlite3.Row
    c.execute('CREATE TABLE IF NOT EXISTS fiches (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT NOT NULL, category TEXT NOT NULL, query TEXT NOT NULL, content TEXT NOT NULL, sources TEXT NOT NULL DEFAULT "[]", created_at TEXT DEFAULT CURRENT_TIMESTAMP)')
    return c

@app.get('/')
def index(): return send_from_directory('static','index.html')

@app.get('/manifest.json')
def manifest(): return send_from_directory('static','manifest.json')

@app.post('/api/research')
def research():
    payload=request.get_json(silent=True) or {}
    question=str(payload.get('question','')).strip()[:1000]
    category=str(payload.get('category','Général'))[:80]
    language=str(payload.get('language','fr'))
    if len(question)<3: return jsonify(error='Veuillez saisir une question plus précise.'),400
    key=os.getenv('OPENAI_API_KEY')
    if not key: return jsonify(error='Clé OPENAI_API_KEY absente sur le serveur. Consultez le README.'),503
    instructions=('Tu es un documentaliste expert en histoire de l’architecture, architecture intérieure et patrimoine. '
                  'Recherche sur le web, distingue faits vérifiés et incertitudes, ne fabrique aucune référence. '
                  'Réponds avec un titre, un résumé, des sections claires, des dates, des exemples, et une bibliographie/liens en fin. '
                  'Lorsque pertinent, traite aussi les liens avec l’architecture algérienne. '
                  'Rédige en arabe.' if language=='ar' else
                  'Tu es un documentaliste expert en histoire de l’architecture, architecture intérieure et patrimoine. '
                  'Recherche sur le web, distingue faits vérifiés et incertitudes, ne fabrique aucune référence. '
                  'Réponds en français avec un titre, un résumé, des sections claires, des dates, des exemples et des sources. '
                  'Lorsque pertinent, traite aussi les liens avec l’architecture algérienne.')
    body={'model':os.getenv('OPENAI_MODEL','gpt-4.1-mini'),'tools':[{'type':'web_search'}],
          'instructions':instructions,'input':f'Catégorie : {category}\nQuestion : {question}'}
    req=urllib.request.Request('https://api.openai.com/v1/responses',data=json.dumps(body).encode(),headers={'Authorization':'Bearer '+key,'Content-Type':'application/json'},method='POST')
    try:
        with urllib.request.urlopen(req,timeout=110) as res: data=json.load(res)
    except urllib.error.HTTPError as e:
        try: detail=json.load(e).get('error',{}).get('message','Erreur API')
        except Exception: detail='Erreur API'
        return jsonify(error=detail),502
    except Exception:
        return jsonify(error='Connexion au service IA impossible. Réessayez.'),502
    texts=[]; sources=[]
    for item in data.get('output',[]):
        if item.get('type')=='message':
            for part in item.get('content',[]):
                if part.get('type')=='output_text':
                    texts.append(part.get('text',''))
                    for ann in part.get('annotations',[]):
                        if ann.get('type')=='url_citation':
                            src={'title':ann.get('title') or ann.get('url'),'url':ann.get('url')}
                            if src['url'] and src not in sources: sources.append(src)
    content='\n\n'.join(texts).strip()
    if not content: return jsonify(error='Aucune réponse textuelle reçue.'),502
    return jsonify(title=question,category=category,query=question,content=content,sources=sources)

@app.get('/api/library')
def library():
    with db() as c:
        return jsonify([dict(r) for r in c.execute('SELECT * FROM fiches ORDER BY id DESC')])

@app.post('/api/library')
def save():
    p=request.get_json(silent=True) or {}
    if not p.get('content') or not p.get('title'): return jsonify(error='Fiche incomplète'),400
    with db() as c:
        cur=c.execute('INSERT INTO fiches (title,category,query,content,sources) VALUES (?,?,?,?,?)',(
            str(p['title'])[:300],str(p.get('category','Général'))[:80],str(p.get('query',''))[:1000],str(p['content'])[:30000],json.dumps(p.get('sources',[]))))
        return jsonify(id=cur.lastrowid),201

@app.delete('/api/library/<int:item_id>')
def delete(item_id):
    with db() as c: c.execute('DELETE FROM fiches WHERE id=?',(item_id,))
    return jsonify(ok=True)

if __name__=='__main__':
    db().close()
    app.run(host='127.0.0.1',port=int(os.getenv('PORT','5000')),debug=False)
