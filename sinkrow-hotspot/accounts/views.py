from django.shortcuts import render, redirect
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
import requests
from django.http import HttpResponse
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db.models import Sum
from .models import RadAcct, UserPackage, Activeusers, RadCheck
userlogin = False

def index(request):

    return render(request, 'index.html')

def login_view(request):
    error = ""
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
        uamip = "10.0.0.1"        # عنوان CoovaChilli
        uamport = "3990"
        userurl = "http://10.0.0.1/accounts/success"  # الصفحة اللي يروح لها بعد الدخول
        if not request.GET.get('res') or request.GET.get('res') == "notyet":
            if RadCheck.objects.filter(username = username).exists():
                if UserPackage.objects.filter(user=RadCheck.objects.get(username = username)).exists():
                    if  UserPackage.objects.get(user=RadCheck.objects.get(username = username)).is_active:
                        return redirect(f'http://{uamip}:{uamport}/logon?username={username}&password={password}&userurl={userurl}')
                    elif not UserPackage.objects.get(user=RadCheck.objects.get(username = username)).is_active and RadCheck.objects.get(username = username).value == password:
                        return redirect(f'http://10.0.0.1/accounts/error/{username}/1')
                    elif RadCheck.objects.get(username = username).value == password:
                        return redirect(f'http://10.0.0.1/accounts/error/{username}/2')
                    # if RadCheck.objects.filter(username = username).exists():
                    #     if UserPackage.objects.filter(user = RadCheck.objects.get(username = username)).exists():
                    #         client = UserPackage.objects.get(user = RadCheck.objects.get(username = username))
                else:
                    return redirect(f'http://10.0.0.1/accounts/error/{username}/2')    
            else:
                return redirect(f'http://10.0.0.1/accounts/error/{username}/2')
        if request.GET.get('res') == 'already':
            print("client is already logedin and redirect to success page")
            return redirect('acc:success')
    else:
        if request.GET.get('res') and request.GET.get('res') == "failed":
            error = "غير مصرح لتلك البيانات بالدخول يرجي التأكد من الأسم وكلمة المرور المرسلين"
        if request.GET.get('res') and request.GET.get('res') == "success":
            return redirect(f"http://10.0.0.1/accounts/success/{request.GET.get('uid')}")
        if request.GET.get('res') and request.GET.get('res') == "already":
            return redirect(f'http://10.0.0.1/accounts/dashboard/{request.GET.get('uid')}')
        # تحتاج للتعديل بحيث تتحول لصفحة إعلام بالخروج و من ثم إمكانية إعادة الدخول مره اخري
        if request.GET.get('res') and request.GET.get('res') == "logoff":
            error = "تم تسجيل الخروج بنجاح يرجي ملئ بيانات المستخدم للتسجيل مره أخري"
            return redirect('http://10.0.0.1:3990')
            
        if request.GET.get('res') or request.GET.get('res') == "notyet" and request.GET.get('uamip') and request.GET.get('uamport') and request.GET.get('challenge') and request.GET.get('userip') and request.GET.get('userurl'):
            return render(request, 'login.html', context={
                'uamip' : request.GET.get('uamip'),
                'uamport' : request.GET.get('uamport'),
                'challenge' : request.GET.get('challenge'),
                'userip' : request.GET.get('userip'),
                'userurl' : request.GET.get('userurl'),
                'error' : error
            })
        else:
            return redirect('http://10.0.0.1:3990')


def add_radius_user(username, password):
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO radcheck (username, attribute, op, value) VALUES (%s, 'Cleartext-Password', ':=', %s)",
            [username, password]
        )

def allow_internet(username):
    with connection.cursor() as cursor:
        cursor.execute(
            "INSERT INTO radreply (username, attribute, op, value) VALUES (%s, 'Framed-IP-Address', '=', '10.0.0.100')",
            [username]
        )


def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        add_radius_user(username, password)
        # allow_internet(username)  # لو حبيت

        return redirect('acc:success')

    return render(request, 'register.html')

def get_user_usage_mb(username):
    usage = RadAcct.objects.filter(username=username).aggregate(
        total_download=Sum('acctinputoctets'),
        total_upload=Sum('acctoutputoctets')
    )
    total = (usage['total_download'] or 0) + (usage['total_upload'] or 0)
    return total / (1024 * 1024)  # إلى ميجابايت

#@login_required
def dashboard(request, username):
    usage = get_user_usage_mb(username)
    limit = UserPackage.objects.get(user=RadCheck.objects.filter(username=username).last()).limit_total_data
    quota = float(limit) - float(usage)
    context = {
        'username': username,
        'quota': int(quota),
    }
    return render(request, 'dashboard.html', context)


def logout_view(request, username):
    client_ip = request.META.get('REMOTE_ADDR')
    if RadAcct.objects.filter(username = username, acctstoptime = None).exists():
        print("existed###############")
        print(username)
        print(client_ip)
        if Activeusers.objects.filter(Radip = client_ip).exists():
            if Activeusers.objects.get(Radip = client_ip).Raduser == RadAcct.objects.filter(username = username, ).last():
                Activeusers.objects.get(Radip = client_ip).delete()
                print(f'the client with {client_ip} is loged out')
                return redirect("http://10.0.0.1:3990/logoff")
            else:
                return redirect("http://10.0.0.1/accounts/username/error/0")
        else:
            return redirect('http://10.0.0.1:3990')
    else:
        return redirect('http://10.0.0.1:3990')
    

def success_view(request, username=""):
    print(f"{username} logged is done correctly")
    data=""
    if not username == "" and not username == " " and not username == None:
        if RadAcct.objects.filter(username = username, acctstoptime = None).exists():
            client_D = RadAcct.objects.filter(username = username, acctstoptime = None).last()
            if not Activeusers.objects.filter(Raduser=RadAcct.objects.filter(username = username, acctstoptime = None).last()).exists():
                Activeusers.objects.create(
                    Raduser = client_D,
                    Radip = request.META.get('REMOTE_ADDR')
                )
                return redirect(f"http://10.0.0.1/accounts/dashboard/{username}")
            else:
                data = RadAcct.objects.filter(username = username, acctstoptime = None).last()
    else:
        data = ""
    return render(request, "success.html", context={
        'data': data,
        'user': username
    })
    
def error_view(request, username,err):
    errors = [
        'غير مصرح لك بالدخول لهذا الرابط',
        'لا يمكنك التسجيل بهذا المستخدم في الوقت الحالي عليك التواصل مع إدارة الشركه للتفعيل',
        'هناك خطأ بكلمة المرور أو المستخدم',
        
    ]
    context = {
        "error": errors[err]
    }
    return render(request, 'error.html', context)
# from .forms import RegisterForm
# from pyrad.dictionary import Dictionary
# import subprocess
# from django.db import connection
# from .models import UserPackage, RadCheck, RadReply
# import uuid

# import hashlib



# RADIUS_SERVER = '127.0.0.1'
# RADIUS_SECRET = b'testing123'
# RADIUS_PORT = 1812
# DICT_PATH = "/home/saske/sinkrow-hotspot/accounts/dict"

'''
Received Access-Request Id 57 from 127.0.0.1:53203 to 127.0.0.1:1812 length 289
(1)   ChilliSpot-Version = "1.6"
(1)   User-Name = "sultan"
(1)   CHAP-Challenge = 0xea1551f4e465c9fb17e30cf3ea71aa56
(1)   CHAP-Password = 0x0067d020fadfb16121cef555e19d42505e
(1)   Service-Type = Login-User
(1)   Acct-Session-Id = "175114367300000001"
(1)   Framed-IP-Address = 10.0.0.2
(1)   NAS-Port-Type = Wireless-802.11
(1)   NAS-Port = 1
(1)   NAS-Port-Id = "00000001"
(1)   Calling-Station-Id = "28-D2-44-37-69-7C"
(1)   Called-Station-Id = "BC-24-11-65-83-89"
(1)   NAS-IP-Address = 10.0.0.1
(1)   NAS-Identifier = "nas01"
(1)   WISPr-Location-ID = "isocc=,cc=,ac=,network=Coova,"
(1)   WISPr-Location-Name = "My_HotSpot"
(1)   WISPr-Logoff-URL = "http://10.0.0.1:3990/logoff"
(1)   Message-Authenticator = 0x98e0322eec61915a68ada3f76a79a9f0
'''
# def login_to_coova(username, password, client_ip, uamip, uamport, challenge, userip):
#     coova_url = "http://10.0.0.1:3990/wwww/cgi-bin/login"  # غير العنوان لو فيه بوابة مختلفة
#     data = {
#         "username": username,
#         "password": password,
#         "ip": client_ip,  # IP المستخدم إذا كان مطلوب
#         "redir": "",      # لو في redirection بعد الدخول
#         "uamip":uamip,
#         "uamport":uamport,
#         "challenge":challenge,
#         "userip":userip,
#         "uamsecret": "testing123"
#     }

#     try:
#         response = requests.post(coova_url, data=data, timeout=5)
#         print(response.text)
#         if "Login Successful" in response.text:
#             return {"success": True, "message": "login is success"}
#         else:
#             return {"success": False, "message": "failed to login", "response": response.text}
#     except requests.RequestException as e:
#         return {"success": False, "message": "خطأ في الاتصال بـ Coova", "error": str(e)}
# UAM_SECRET = "testing123"  # نفس اللي في /etc/chilli/config
# UAM_IP = "10.0.0.1"
# UAM_PORT = 3990
# def chilli_login(username, password, challenge, userurl="http://1.0.0.0/"):

#     login_url = f"http://{UAM_IP}:{UAM_PORT}/logon"
#     payload = {
#         "username": username,
#         "password": password,
#         "userurl": userurl
#     }

#     response = requests.post(login_url, params=payload)
#     return response.status_code, response.text
# import hashlib

# def chap_response(chap_id, password, chap_challenge):
#     # chap_id: string in hex (مثلاً "00")
#     # chap_challenge: string in hex (مثلاً "a6ad54...")
#     chap_id_byte = bytes.fromhex(chap_id)
#     password_byte = password.encode()
#     challenge_byte = bytes.fromhex(chap_challenge)

#     chap_response_raw = hashlib.md5(chap_id_byte + password_byte + challenge_byte).hexdigest()
#     return chap_response_raw


# def authenticate_radius(username, password):
#     import pyrad.packet
#     from pyrad.client import Client
#     from pyrad.dictionary import Dictionary

#     client = Client(server=RADIUS_SERVER, secret=RADIUS_SECRET, dict=Dictionary(DICT_PATH))
#     req = client.CreateAuthPacket(code=pyrad.packet.AccessRequest, User_Name=username)
#     req["User-Password"] = req.PwCrypt(password)

#     try:
#         reply = client.SendPacket(req)
#         return reply.code == pyrad.packet.AccessAccept
#     except:
#         return False

# def apply_radius_config(user):
#     plan = user.plan

#     with connection.cursor() as cursor:
#         # Step 1: حفظ كلمة المرور
#         cursor.execute(
#             "INSERT INTO radcheck (username, attribute, op, value) VALUES (%s, 'Cleartext-Password', ':=', %s)",
#             [user.username, user.password]
#         )

#         # Step 2: إضافة السرعة
#         cursor.execute(
#             "INSERT INTO radreply (username, attribute, op, value) VALUES (%s, 'WISPr-Bandwidth-Max-Down', ':=', %s)",
#             [user.username, plan.download_speed]
#         )
#         cursor.execute(
#             "INSERT INTO radreply (username, attribute, op, value) VALUES (%s, 'WISPr-Bandwidth-Max-Up', ':=', %s)",
#             [user.username, plan.upload_speed]
#         )

#         # Step 3: جلسة مؤقتة (اختياري)
#         if plan.session_timeout:
#             cursor.execute(
#                 "INSERT INTO radreply (username, attribute, op, value) VALUES (%s, 'Session-Timeout', ':=', %s)",
#                 [user.username, str(plan.session_timeout)]
#             )



# import subprocess

# def applyspeed(ip, download, upload, interface="tun0", class_id="12"):
#     try:
#         # 1. Add root qdisc (if not exists)
#         subprocess.run([
#             "sudo", "tc", "qdisc", "add", "dev", interface, "root",
#             "handle", "1:", "htb", "default", class_id
#         ], stderr=subprocess.DEVNULL)

#         # 2. Add parent class (main class with high ceil)
#         subprocess.run([
#             "sudo", "tc", "class", "add", "dev", interface, "parent", "1:",
#             "classid", "1:1", "htb", "rate", f"{upload}", "ceil", f"{upload}"
#         ], stderr=subprocess.DEVNULL)

#         # 3. Add child class for this user (we use classid 1:12 as default)
#         subprocess.run([
#             "sudo", "tc", "class", "add", "dev", interface, "parent", "1:1",
#             "classid", f"1:{class_id}", "htb", "rate", f"{download}", "ceil", f"{download}"
#         ], stderr=subprocess.DEVNULL)

#         # 4. Apply filter for the IP to match class
#         subprocess.run([
#             "sudo", "tc", "filter", "add", "dev", interface, "protocol", "ip",
#             "parent", "1:0", "prio", "1", "u32", "match", "ip", "src", ip,
#             "flowid", f"1:{class_id}"
#         ], stderr=subprocess.DEVNULL)

#         print(f"[✓] Applied {ip} => Download: {download}kbps, Upload: {upload}kbps")

#     except Exception as e:
#         print(f"[✗] Error: {e}")

# def remove_tc_filter_by_ip(interface, ip):
#     try:
#         subprocess.run([
#             "sudo", "tc", "filter", "del",
#             "dev", interface,
#             "protocol", "ip",
#             "parent", "1:0",
#             "prio", "1",
#             "u32", "match", "ip", "src", ip
#         ], check=True)
#         print(f"[✓] Deleted filter for IP: {ip}")
#     except subprocess.CalledProcessError as e:
#         print(f"[!] Failed to delete filter for IP: {ip}")

#---------------------------
#---------------------------
#---------------------------
#---------------------------

# def get_mac_from_chilli_query(client_ip):
#     try:
#         result = subprocess.check_output(['sudo', 'chilli_query', 'list']).decode()
#         for line in result.splitlines():
#             if client_ip in line:
#                 parts = line.split()
#                 return parts[0]  # أول عمود هو الـ MAC
#     except Exception as e:
#         return f"Error: {e}"


# def send_accounting_start(username, client_ip, mac_address, secret="testing123", nas_ip="127.0.0.1", radius_port=1813):
#     acct_session_id = str(uuid.uuid4())

#     # بناء محتوى الـ Accounting packet
#     packet = f"""
# User-Name = "{username}"
# NAS-IP-Address = {nas_ip}
# Acct-Status-Type = Start
# WISPr-Bandwidth-Max-Down = "{RadReply.objects.get(username = username, attribute='WISPr-Bandwidth-Max-Down').value}"
# WISPr-Bandwidth-Max-Up = "{RadReply.objects.get(username = username, attribute='WISPr-Bandwidth-Max-Up').value}"
# Acct-Session-Id = "{acct_session_id}"
# Framed-IP-Address = {client_ip}
# Calling-Station-Id = "{mac_address}"
# """

#     try:
#         result = subprocess.run(
#             ['sudo', 'radclient', '-x', f'{nas_ip}:{radius_port}', 'acct', secret],
#             input=packet.encode('utf-8'),
#             stdout=subprocess.PIPE,
#             stderr=subprocess.PIPE,
#             check=True
#         )
#         return result.stdout.decode('utf-8')
#     except subprocess.CalledProcessError as e:
#         return f"Error sending accounting packet: {e.stderr.decode('utf-8')}"
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
######################### Final Login Function CLEARTEXT Password ##########################
######################### Final Login Function CLEARTEXT Password ##########################
######################### Final Login Function CLEARTEXT Password ##########################
######################### Final Login Function CLEARTEXT Password ##########################
######################### Final Login Function CLEARTEXT Password ##########################
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
#-------------------------------------------------------------------------------------------
# @csrf_exempt
# def login_view(request):
#     if request.method == 'POST':
#         username = request.POST.get('username')
#         password = request.POST.get('password')
#         print('the client try connecting by username is: ' + username + ' and his password is: ' + password)
#         uamip = request.POST.get('uamip')
#         uamport = request.POST.get('uamport')
#         userip = request.POST.get('userip')
#         userurl = request.POST.get('userurl')
#         return redirect(f'http://{uamip}:{uamport}/logon?username={username}&password={password}&userurl={userurl}')

#     else:
#         uamip = request.GET.get('uamip')
#         uamport = request.GET.get('uamport')
#         challenge = request.GET.get('challenge')
#         userip = request.GET.get('userip')
#         userurl = request.GET.get('userurl')
#         return render(request, 'login.html', context={
#             'uamip' : uamip,
#             'uamport' : uamport,
#             'challenge' : challenge,
#             'userip' : userip,
#             'userurl' : userurl,
#         })

# def open_internet(ip):
#     cmd = ["sudo", "/usr/sbin/chilli_query", "authorize", "ip", ip]
#     subprocess.run(cmd)
#     print("internet is running")


