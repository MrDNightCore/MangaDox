import http.cookiejar, urllib.request, urllib.parse, re
cj = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
url = 'http://127.0.0.1:8000/users/registers/'
print('GET register page...')
r = opener.open(url)
html = r.read().decode('utf-8', 'ignore')
# find csrf token
m = re.search(r"name=['\"]csrfmiddlewaretoken['\"] value=['\"]([^'\"]+)['\"]", html)
if not m:
    print('CSRF token not found')
    raise SystemExit(1)
token = m.group(1)
print('csrf:', token[:8]+'...')

# Prepare data
from datetime import datetime
suffix = datetime.now().strftime('%f')
username = 'testuser_ci_'+suffix
email = 'testuser_ci_'+suffix+'@example.com'
password = 'StrongPass!234'
post_data = {
    'username': username,
    'email': email,
    'password': password,
    'confirm_password': password,
    'csrfmiddlewaretoken': token
}
encoded = urllib.parse.urlencode(post_data).encode()
req = urllib.request.Request(url, data=encoded, headers={'Referer': url})
resp = opener.open(req, timeout=15)
print('POST response code:', resp.getcode())
body = resp.read().decode('utf-8','ignore')
if 'Registration successful' in body or 'Registration successful!' in body:
    print('Registration appears successful (response body contains success message).')
    # Try login with the same credentials
    print('Attempting login with the new user...')
    login_url = 'http://127.0.0.1:8000/users/login/'
    r2 = opener.open(login_url)
    html2 = r2.read().decode('utf-8','ignore')
    m2 = re.search(r"name=['\"]csrfmiddlewaretoken['\"] value=['\"]([^'\"]+)['\"]", html2)
    if not m2:
        print('Login CSRF token not found')
    else:
        token2 = m2.group(1)
        post_login = {
            'username': username,
            'password': password,
            'csrfmiddlewaretoken': token2
        }
        req2 = urllib.request.Request(login_url, data=urllib.parse.urlencode(post_login).encode(), headers={'Referer': login_url})
        resp2 = opener.open(req2, timeout=15)
        body2 = resp2.read().decode('utf-8','ignore')
        if 'Welcome back' in body2 or 'Welcome back,' in body2:
            print('Login appears successful (found welcome message).')
        else:
            print('Login response status:', resp2.getcode())
            # try to detect a redirect to home
            print('Login response snippet:')
            print(body2[:800])
else:
    # extract any messages lists
    msgs = re.findall(r"<ul class=\"messages\".*?</ul>", body, flags=re.S)
    site_msgs = re.findall(r"<div class=\"site-messages\".*?</div>", body, flags=re.S)
    if msgs:
        print('Found messages block:')
        print(msgs[0])
    elif site_msgs:
        print('Found site-messages block:')
        print(site_msgs[0][:1000])
    else:
        print('No messages found; saving first 1000 chars of body:')
        print(body[:1000])
