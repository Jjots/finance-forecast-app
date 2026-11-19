from flask import Flask, render_template, jsonify, request
from datetime import datetime
app = Flask(__name__)

companies = [
 {"name":"Сбербанк","ticker":"SBER","inn":"7707083893","industry":"Финансы","revenue":"3,2 трлн ₽","profit":"1,05 трлн ₽","change":8.4,"risk":"Низкий"},
 {"name":"Газпром","ticker":"GAZP","inn":"7736050003","industry":"Энергетика","revenue":"8,1 трлн ₽","profit":"629 млрд ₽","change":-2.1,"risk":"Средний"},
 {"name":"Яндекс","ticker":"YDEX","inn":"7736207543","industry":"ИТ","revenue":"1,1 трлн ₽","profit":"92 млрд ₽","change":14.7,"risk":"Средний"},
 {"name":"Лукойл","ticker":"LKOH","inn":"7744000518","industry":"Энергетика","revenue":"7,4 трлн ₽","profit":"1,2 трлн ₽","change":5.2,"risk":"Низкий"},
 {"name":"Норникель","ticker":"GMKN","inn":"7740000076","industry":"Металлургия","revenue":"1,3 трлн ₽","profit":"181 млрд ₽","change":-4.3,"risk":"Высокий"},
 {"name":"МТС","ticker":"MTSS","inn":"7740000076","industry":"Телеком","revenue":"675 млрд ₽","profit":"41 млрд ₽","change":6.1,"risk":"Средний"},
]
@app.route('/')
def index(): return render_template('index.html', companies=companies)
@app.route('/api/companies')
def search_companies():
 q=request.args.get('q','').lower(); industry=request.args.get('industry','')
 result=[c for c in companies if (q in c['name'].lower() or q in c['inn'] or q in c['ticker'].lower()) and (not industry or c['industry']==industry)]
 return jsonify(result)
@app.route('/api/forecast', methods=['POST'])
def forecast():
 payload=request.json or {}
 return jsonify({"status":"ready","company":payload.get('company','Сбербанк'),"model":"XGBoost","metric":"Выручка","horizon":payload.get('horizon','квартал'),"quality":{"MAE":"4.8%","RMSE":"6.2%","MAPE":"5.1%"},"demo":True})
@app.route('/api/admin/retrain', methods=['POST'])
def retrain(): return jsonify({"status":"queued","message":"Задание на переобучение создано (демо)."})
@app.route('/api/admin/upload', methods=['POST'])
def upload(): return jsonify({"status":"accepted","message":"Файл принят для проверки (демо)."})
@app.route('/api/users')
def users(): return jsonify([{"name":"Иван Петров","email":"i.petrov@example.ru","role":"Аналитик","status":"Активен"},{"name":"Мария Смирнова","email":"m.smirnova@example.ru","role":"Риск-менеджер","status":"Активен"},{"name":"Алексей Волков","email":"a.volkov@example.ru","role":"Инвестор","status":"Активен"}])
if __name__=='__main__': app.run(debug=True)
