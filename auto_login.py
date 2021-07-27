from webbot import Browser

url = 'https://kite.zerodha.com/'
user_name   = 'XZ7730' 
password    = '' 
pin         = ''

web = Browser()
web.go_to(url)
web.type(user_name , into='User ID')
web.type(password , into='Password')
web.click('Login')
web.type(pin , into='PIN')
web.click('Continue')
tittle = web.get_title()
print(tittle)
