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
