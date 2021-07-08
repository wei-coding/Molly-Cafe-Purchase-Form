from flask import Flask, render_template, request, redirect, send_from_directory, url_for, jsonify
from lib.account import customer, Status, search_name, login_check, Hint
from lib import account
from lib.goods import GoodsManager

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/form', methods=['GET', 'POST'])
def form():
    user_hash = request.cookies.get('user')
    if request.method == 'GET':
        if user_hash is not None:
            name = search_name(user_hash)
            return render_template('form.html', welcome=name+'先生/小姐，您好！')
        else:
            return redirect('/login')
    else:
        data = account.search_data(user_hash)['purchase_record']
        n = int(request.form.get('n-items'))
        gm = GoodsManager()
        for i in range(n):
            purchased = int(request.form.get('num-' + str(i)))
            if n > len(data) or data[i] == 0:
                gm.new_order(i, purchased)
                account.customer_order(user_hash,
                    {
                        'items': i,
                        'num-items': purchased,
                    }
                )
            else:
                gm.new_order(i, purchased - data[i])
                account.customer_order(user_hash,
                    {
                        'items': i,
                        'num-items': purchased,
                    }
                )
        return redirect('/form?send=1')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login', methods=['POST'])
def signin():
    name = request.form.get('name')
    tele = request.form.get('tele')
    print(name, tele)
    status = 'success'
    s, cookie = customer(name, tele)
    if s == Status.SignInSuccess:
        status = 'signin'
    elif s == Status.SignUpSuccess:
        status = 'signup'
    else:
        status = 'error'
        return redirect('/login?status=' + status)
    resp = redirect('/login?status=' + status)
    resp.set_cookie('user', cookie)
    return resp

@app.route('/logout')
def logout():
    resp = redirect('/login')
    resp.set_cookie('user', '', expires=0)
    return resp

@app.route('/admin', methods=['GET', 'POST'])
def admin():
    if request.method == 'GET':
        id = request.cookies.get('user')
        if account.check_admin(id) == Hint.LoginSuccess:
            return redirect('/myconsole')
        else:
            return render_template('admin.html')
    else:
        # account and password check
        username = request.form.get('name')
        password = request.form.get('password')
        if username and password:
            result, id = login_check(username, password)
            if result == Hint.LoginSuccess:
                resp = redirect('/myconsole')
                resp.set_cookie('user', id)
                return resp
        return redirect('/admin?status=error')

@app.route('/myconsole')
def console():
    id = request.cookies.get('user')
    if account.check_admin(id) == Hint.LoginSuccess:
        return render_template('console.html')
    else:
        return '你沒有權限瀏覽此網頁<br>' + '<a href="/">回首頁</a>'

@app.route('/myconsole/edit')
def edit():
    id = request.cookies.get('user')
    if account.check_admin(id) == Hint.LoginSuccess:
        return render_template('console_edit.html')
    else:
        return '你沒有權限瀏覽此網頁<br>' + '<a href="/">回首頁</a>'

@app.route('/myconsole/table')
def table():
    id = request.cookies.get('user')
    if account.check_admin(id) == Hint.LoginSuccess:
        return render_template('console_table.html')
    else:
        return '你沒有權限瀏覽此網頁<br>' + '<a href="/">回首頁</a>'

@app.route('/myconsole/edit', methods=['POST'])
def edit_backend():
    num = int(request.form.get('num'))
    gm = GoodsManager()
    gm.clear()
    for i in range(num):
        name = request.form.get('name-' + str(i))
        img = request.files['img-' + str(i)]
        expires = request.form.get('exipres')
        img.save('statics/img-' + str(i+1) + '.jpg')
        description = request.form.get('description-' + str(i))
        limit = int(request.form.get('limit-' + str(i)))
        print(name, description, limit)
        gm.revise_goods(i, name, 'img-'+str(i+1), description, limit, expires)
        account.reset_all_order()
    return redirect('/myconsole/edit')

@app.route('/all_goods')
def all_goods():
    return send_from_directory('lib', 'goods.json')

@app.route('/customer_data')
def customer_data():
    user_hash = request.cookies.get('user')
    data = account.search_data(user_hash)
    if data:
        return jsonify(data)
    else:
        return jsonify({})

@app.route('/all_customer_data')
def all_customer_data():
    id = request.cookies.get('user')
    if account.check_admin(id) == Hint.LoginSuccess:
        return jsonify(account.get_all_customer_data())
    else:
        return jsonify({})

@app.route('/statics/<path:path>')
def statics_file(path):
    return send_from_directory('statics', path)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)