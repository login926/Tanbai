from time import time, sleep
from random import random
import os
import re
import time
import sys
import requests
import subprocess
from prettytable import PrettyTable

QRImgPath = os.path.split(os.path.realpath(__file__))[0] + os.sep + 'webQQqr.png'
sess = requests.Session()
sourceURL = 'https://ti.qq.com/cgi-node/honest-say/receive/mine'
js_ver = '10226'

def genqrtoken(qrsig):
        e = 0
        for i in range(0, len(qrsig)):
            e += (e << 5) + ord(qrsig[i])
        qrtoken = (e & 2147483647)
        return str(qrtoken)

def genbkn(skey):
        b = 5381
        for i in range(0, len(skey)):
            b += (b << 5) + ord(skey[i])
        bkn = (b & 2147483647)
        return str(bkn)

def genqq(qq):
    en = ('oe','oK','ow','oi','7e','7K','7w','7i','Ne','NK',
    		'on','ov','oc','oz','7n','7v','7c','7z','Nn','Nv',
    		'n','b','-','o','v','a','C','S','c','E',
    		'z','d','A','i','P','k','s','I','F','q')
    qq = qq.replace('4','a').replace('6','b').replace('5','d')
    for i in range(len(en)) :
    	qq = qq.replace(en[i], str(i%10), 10)
    qq = qq.replace('l','7')
    return qq


headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/65.0.3325.181 Safari/537.36'
        }

url = 'http://ui.ptlogin2.qq.com/cgi-bin/login'
params = {
                'appid': '715030901',
                'daid': '73',
                'pt_no_auth': '1',
            }
loginresp = sess.get(url, params=params, timeout=1000)
sess.headers.update({'Referer': url})
url = 'http://ptlogin2.qq.com/ptqrshow'
params = {
                'appid': '715030901',
                'e': '2',
                'l': 'M',
                's': '3',
                'd': '72',
                'v': '4',
                't': '%.17f' % (random()),
                'daid': '73'
            }
qrresp = sess.get(url, params=params, timeout=1000)
with open(QRImgPath, 'wb') as f :
        f.write(qrresp.content)
        f.close()

if sys.platform.find('darwin') >= 0:
    subprocess.call(['open', QRImgPath])
elif sys.platform.find('linux') >= 0:
    subprocess.call(['xdg-open', QRImgPath])
else:
    os.startfile(QRImgPath)
print('请使用手机 QQ 扫描二维码以登录')


status = 0
while True :
        #login_sig = sess.cookies['pt_login_sig']
        qrsig = sess.cookies['qrsig']
        errorMsg = ''
        url = 'http://ptlogin2.qq.com/ptqrlogin'
        params = {
                'u1': sourceURL,
                'ptqrtoken': genqrtoken(qrsig),
                'ptredirect': '1',
                'h': '1',
                't': '1',
                'g': '1',
                'from_ui': '1',
                'ptlang': '2052',
                'action': '0-0-%d' % (time.time() * 1000),
                'js_ver': js_ver,
                'js_type': '1',
                #'login_sig': login_sig,
                'pt_uistyle': '40',
                'aid': '715030901',
                'daid': '73'
                }
        resp = sess.get(url, params=params, timeout=1000,headers = headers)
        code = re.findall(r'(?<=ptuiCB\(\').*?(?=\',)',resp.text)[0]
        if code == '67' and status == 0:
            print('扫码成功，请确认登录')
            status = 1
        if code == '0' :
            print('登录成功...')
            break
        elif code == '65' :
            print('二维码失效, 请重新启动程序')

os.remove(QRImgPath)
qq = re.findall(r'(?<=uin=).*?(?=&service)',resp.text)[0]
print(qq,'登陆成功')
skey = sess.cookies['skey']
print('正在获取')

tanbai_url = sourceURL + '?_client_version=0.0.79&token=' + genbkn(skey)
tanbai = sess.get(tanbai_url,headers = headers,timeout=1000)
tanbai_EncodeUin = re.findall(r'(?<=fromEncodeUin\":\").*?(?=\",\"fromFaceUrl)',tanbai.text)
tanbai_topicName = re.findall(r'(?<=topicName\":\").*?(?=\",\"timestamp)',tanbai.text)

row = PrettyTable()
row.field_names = ["QQ","备注","坦白说"]
i = 0
qzone_url = 'https://h5.qzone.qq.com/proxy/domain/r.qzone.qq.com/cgi-bin/user/cgi_personal_card?uin='
while i<len(tanbai_EncodeUin):
    friendrealqq = genqq(tanbai_EncodeUin[i].replace('*S1*',''))
    tanbai = tanbai_topicName[i]
    user_qzone = qzone_url + friendrealqq + '&g_tk=' + genbkn(skey)
    resp = sess.get(user_qzone,headers = headers)
    nick =  re.findall(r'(?<=realname\":\").*?(?=\",)',resp.text)[0]
    row.add_row([friendrealqq,nick,tanbai])
    i = i + 1
print(row)