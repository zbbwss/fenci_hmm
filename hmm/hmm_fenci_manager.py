# -*- coding: utf-8 -*-
# Created by 'Zhou Bingbing'  on 2019/8/5

from flask import Flask, request

from test import HMM

app = Flask(__name__)


@app.route('/hmm',methods=['GET', 'POST'])
def Hmm():
    text=request.args.get('text')
    hmm = HMM()
    res = hmm.cut(text)
    return str(list(res))


if __name__ == '__main__':
    app.run(port=10001,host='0.0.0.0')
