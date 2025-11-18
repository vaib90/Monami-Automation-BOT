from aiohttp import (
    ClientResponseError,
    ClientSession,
    ClientTimeout
)
from aiohttp_socks import ProxyConnector
from datetime import datetime
from colorama import *
import asyncio, random, json, os, pytz, time
import functools
from seleniumbase import SB 

wib = pytz.timezone('Asia/Ho_Chi_Minh')

USER_AGENT = [
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36",
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
  "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
  "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36",
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0",
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0",
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:121.0) Gecko/20100101 Firefox/121.0",
  "Mozilla/5.0 (X11; Linux x86_64; rv:121.0) Gecko/20100101 Firefox/121.0",
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0",
  "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15",
  "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 OPR/106.0.0.0"
]

HEADERS = {
    "Accept": "application/json, text/plain, */*",
    "Accept-Language": "id-ID,id;q=0.9,en-US;q=0.8,en;q=0.7",
    "Origin": "https://monami.network",
    "Referer": "https://monami.network/",
    "Sec-Fetch-Dest": "empty",
    "Sec-Fetch-Mode": "cors",
    "Sec-Fetch-Site": "same-site",
    "User-Agent": random.choice(USER_AGENT)
}

class Monami:
    def __init__(self) -> None:
        self.HEADERS = {}
        self.BASE_API = "https://api.monami.network"
        self.proxies = []
        self.proxy_index = 0
        self.account_proxies = {}
        self.password = {}
        self.access_tokens = {}
        self.tokens_output_path = os.path.join(os.getcwd(), "tokens.txt")

    def clear_terminal(self):
        os.system('cls' if os.name == 'nt' else 'clear')

    def log(self, message):
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}{message}",
            flush=True
        )

    def welcome(self):
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "\n" + "═" * 60)
        print(Fore.GREEN + Style.BRIGHT + "    ⚡ Tự động kết nối Node Ping BOT ⚡")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
        print(Fore.YELLOW + Style.BRIGHT + "    🧠 Dự án    : Monami - Bot tự động")
        print(Fore.YELLOW + Style.BRIGHT + "    🌐 Trạng thái : Đang hoạt động...")
        print(Fore.CYAN + Style.BRIGHT + "    ────────────────────────────────")
        print(Fore.LIGHTGREEN_EX + Style.BRIGHT + "═" * 60 + "\n")

    def format_seconds(self, seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02}:{int(minutes):02}:{int(seconds):02}"

    def load_accounts(self):
        filename = "accounts.json"
        try:
            if not os.path.exists(filename):
                self.log(f"{Fore.RED}Không tìm thấy file {filename}.{Style.RESET_ALL}")
                return

            with open(filename, 'r') as file:
                data = json.load(file)
                if isinstance(data, list):
                    return data
                return []
        except json.JSONDecodeError:
            return []

    async def load_proxies(self, use_proxy_choice: int):
        filename = "proxy.txt"
        try:
            if use_proxy_choice == 1:
                async with ClientSession(timeout=ClientTimeout(total=30)) as session:
                    async with session.get("https://api.proxyscrape.com/v4/free-proxy-list/get?request=display_proxies&proxy_format=protocolipport&format=text") as response:
                        response.raise_for_status()
                        content = await response.text()
                        with open(filename, 'w') as f:
                            f.write(content)
                        self.proxies = [line.strip() for line in content.splitlines() if line.strip()]
            else:
                if not os.path.exists(filename):
                    self.log(f"{Fore.RED + Style.BRIGHT}Không tìm thấy file {filename}.{Style.RESET_ALL}")
                    return
                with open(filename, 'r') as f:
                    self.proxies = [line.strip() for line in f.read().splitlines() if line.strip()]

            if not self.proxies:
                self.log(f"{Fore.RED + Style.BRIGHT}Không tìm thấy proxy nào.{Style.RESET_ALL}")
                return

            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Tổng số proxy  : {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(self.proxies)}{Style.RESET_ALL}"
            )

        except Exception as e:
            self.log(f"{Fore.RED + Style.BRIGHT}Lỗi khi tải proxy: {e}{Style.RESET_ALL}")
            self.proxies = []

    def check_proxy_schemes(self, proxies):
        schemes = ["http://", "https://", "socks4://", "socks5://"]
        if any(proxies.startswith(scheme) for scheme in schemes):
            return proxies
        return f"http://{proxies}"

    def get_next_proxy_for_account(self, email):
        if email not in self.account_proxies:
            if not self.proxies:
                return None
            proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
            self.account_proxies[email] = proxy
            self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return self.account_proxies[email]

    def rotate_proxy_for_account(self, email):
        if not self.proxies:
            return None
        proxy = self.check_proxy_schemes(self.proxies[self.proxy_index])
        self.account_proxies[email] = proxy
        self.proxy_index = (self.proxy_index + 1) % len(self.proxies)
        return proxy

    def mask_account(self, account):
        if "@" in account:
            local, domain = account.split('@', 1)
            mask_account = local[:3] + '*' * 3 + local[-3:]
            return f"{mask_account}@{domain}"

        mask_account = account[:3] + '*' * 3 + account[-3:]
        return mask_account

    def print_message(self, account, proxy, color, message):
        self.log(
            f"{Fore.CYAN + Style.BRIGHT}[ Tài khoản:{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} {self.mask_account(account)} {Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT} Proxy: {Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT}{proxy}{Style.RESET_ALL}"
            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}Trạng thái:{Style.RESET_ALL}"
            f"{color + Style.BRIGHT} {message} {Style.RESET_ALL}"
            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
        )

    def print_question(self):
        while True:
            try:
                print(f"{Fore.WHITE + Style.BRIGHT}1. Chạy với proxy miễn phí từ Proxyscrape{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}2. Chạy với proxy riêng{Style.RESET_ALL}")
                print(f"{Fore.WHITE + Style.BRIGHT}3. Chạy không dùng proxy{Style.RESET_ALL}")
                choose = int(input(f"{Fore.BLUE + Style.BRIGHT}Chọn [1/2/3] -> {Style.RESET_ALL}").strip())

                if choose in [1, 2, 3]:
                    proxy_type = (
                        "với proxy miễn phí Proxyscrape" if choose == 1 else 
                        "với proxy riêng" if choose == 2 else 
                        "không dùng proxy"
                    )
                    print(f"{Fore.GREEN + Style.BRIGHT}Đã chọn chạy {proxy_type}.{Style.RESET_ALL}")
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Vui lòng nhập 1, 2 hoặc 3.{Style.RESET_ALL}")
            except ValueError:
                print(f"{Fore.RED + Style.BRIGHT}Dữ liệu không hợp lệ. Vui lòng nhập số (1, 2 hoặc 3).{Style.RESET_ALL}")

        rotate = False
        if choose in [1, 2]:
            while True:
                rotate = input(f"{Fore.BLUE + Style.BRIGHT}Tự động đổi proxy khi lỗi? [y/n] -> {Style.RESET_ALL}").strip()

                if rotate in ["y", "n"]:
                    rotate = rotate == "y"
                    break
                else:
                    print(f"{Fore.RED + Style.BRIGHT}Dữ liệu không hợp lệ. Nhập 'y' hoặc 'n'.{Style.RESET_ALL}")

        return choose, rotate

    async def check_connection(self, email: str, proxy=None):
        connector = ProxyConnector.from_url(proxy) if proxy else None
        try:
            async with ClientSession(connector=connector, timeout=ClientTimeout(total=30)) as session:
                async with session.post(url="http://ip-api.com/json") as response:
                    response.raise_for_status()
                    return await response.json()
        except (Exception, ClientResponseError) as e:
            self.print_message(email, proxy, Fore.RED, f"Kết nối không ổn định: {Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}")
            return None

    def _seleniumbase_login_sync(self, email: str, password: str, max_retries: int, delay_between_retries: int):
        login_url = "https://monami.network/signin"
        for attempt in range(max_retries):
            self.log(f"{Fore.CYAN}Đang thử đăng nhập bằng SeleniumBase cho {email} (Lần thử {attempt + 1}/{max_retries}){Style.RESET_ALL}")
            try:
                with SB(uc=True, xvfb=True, headless=True) as sb:
                    sb.uc_open(login_url)
                    sb.type('input[name="email"]', email)
                    sb.type('input[name="password"]', password)
                    sb.uc_click('button:contains("Sign In")')
                    sb.sleep(5) 

                    access_token = None
                    all_cookies = sb.get_cookies()
                    for cookie in all_cookies:
                        if cookie.get('name') == 'accessToken':
                            access_token = cookie.get('value')
                            break

                    if access_token:
                        return {"accessToken": access_token}
                    else:
                        self.log(f"{Fore.RED}Không tìm thấy access token cho {email} sau khi đăng nhập.{Style.RESET_ALL}")

            except Exception as e:
                self.log(f"{Fore.RED}Lỗi khi đăng nhập bằng SeleniumBase cho {email}: {str(e)}{Style.RESET_ALL}")

            if attempt < max_retries - 1:
                self.log(f"{Fore.YELLOW}Đợi {delay_between_retries} giây trước khi thử lại...{Style.RESET_ALL}")
                time.sleep(delay_between_retries)
            else:
                self.log(f"{Fore.RED}Đăng nhập bằng SeleniumBase thất bại cho {email} sau {max_retries} lần thử.{Style.RESET_ALL}")
        return None

    def _write_token(self, email: str, token: str):
        with open(self.tokens_output_path, "a") as f:
            f.write(f"{email}:{token}\n")
        self.log(f"{Fore.GREEN}Token cho {email} đã được lưu vào {self.tokens_output_path}{Style.RESET_ALL}")

    async def user_login(self, email: str, proxy=None, retries=5):
        loop = asyncio.get_event_loop()
        login_result = await loop.run_in_executor(
            None,
            functools.partial(self._seleniumbase_login_sync, email, self.password[email], retries, 5)
        )

        if login_result and "accessToken" in login_result:
            self.access_tokens[email] = login_result["accessToken"]
            self._write_token(email, login_result["accessToken"])
            self.print_message(email, proxy, Fore.GREEN, "Đăng nhập thành công (qua SeleniumBase)")
            return login_result
        else:
            self.print_message(email, proxy, Fore.RED, "Đăng nhập thất bại (qua SeleniumBase sau nhiều lần thử)")
            return None

    async def user_info(self, email: str, use_proxy: bool, rotate_proxy: bool, proxy=None, retries=5):
        url = f"{self.BASE_API}/users"
        headers = self.HEADERS[email].copy()
        headers["Authorization"] = f"Bearer {self.access_tokens[email]}"
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers, ssl=False) as response:
                        if response.status == 401:
                            self.print_message(email, proxy, Fore.YELLOW, "Token hết hạn, đang thử đăng nhập lại.")
                          
                            await self.process_user_login(email, use_proxy, rotate_proxy)
                            headers["Authorization"] = f"Bearer {self.access_tokens[email]}"
                            continue
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(email, proxy, Fore.RED, f"Lấy thông tin người dùng thất bại: {Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}")

        return None

    async def perform_checkin(self, email: str, use_proxy: bool, rotate_proxy: bool, proxy=None, retries=5):
        url = f"{self.BASE_API}/users/checkin"
        data = json.dumps({"email":email})
        headers = self.HEADERS[email].copy()
        headers["Authorization"] = f"Bearer {self.access_tokens[email]}"
        headers["Content-Length"] = str(len(data))
        headers["Content-Type"] = "application/json"
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.patch(url=url, headers=headers, data=data, ssl=False) as response:
                        if response.status == 401:
                            self.print_message(email, proxy, Fore.YELLOW, "Token hết hạn, đang thử đăng nhập lại.")
                            await self.process_user_login(email, use_proxy, rotate_proxy)
                            headers["Authorization"] = f"Bearer {self.access_tokens[email]}"
                            continue
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(email, proxy, Fore.RED, f"Check-In thất bại: {Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}")

        return None

    async def connect_node(self, email: str, use_proxy: bool, rotate_proxy: bool, proxy=None, retries=5):
        url = f"{self.BASE_API}/points/update-last-active"
        data = json.dumps({"email":email})
        headers = self.HEADERS[email].copy()
        headers["Authorization"] = f"Bearer {self.access_tokens[email]}"
        headers["Content-Length"] = str(len(data))
        headers["Content-Type"] = "application/json"
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.patch(url=url, headers=headers, data=data, ssl=False) as response:
                        if response.status == 401:
                            self.print_message(email, proxy, Fore.YELLOW, "Token hết hạn, đang thử đăng nhập lại.")
                            await self.process_user_login(email, use_proxy, rotate_proxy)
                            headers["Authorization"] = f"Bearer {self.access_tokens[email]}"
                            continue
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(email, proxy, Fore.RED, f"Lite Node không kết nối: {Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}")

        return None

    async def update_point(self, email: str, use_proxy: bool, rotate_proxy: bool, proxy=None, retries=5):
        url = f"{self.BASE_API}/points/update-point?email={email}"
        headers = self.HEADERS[email].copy()
        headers["Authorization"] = f"Bearer {self.access_tokens[email]}"
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers, ssl=False) as response:
                        if response.status == 401:
                            self.print_message(email, proxy, Fore.YELLOW, "Token hết hạn, đang thử đăng nhập lại.")
                            await self.process_user_login(email, use_proxy, rotate_proxy)
                            headers["Authorization"] = f"Bearer {self.access_tokens[email]}"
                            continue
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(email, proxy, Fore.RED, f"Cập nhật điểm thất bại: {Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}")

        return None

    async def task_lists(self, email: str, use_proxy: bool, rotate_proxy: bool, proxy=None, retries=5):
        url = f"{self.BASE_API}/tasks/?email={email.replace('@', '%40')}"
        headers = self.HEADERS[email].copy()
        headers["Authorization"] = f"Bearer {self.access_tokens[email]}"
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.get(url=url, headers=headers, ssl=False) as response:
                        if response.status == 401:
                            self.print_message(email, proxy, Fore.YELLOW, "Token hết hạn, đang thử đăng nhập lại.")
                            await self.process_user_login(email, use_proxy, rotate_proxy)
                            headers["Authorization"] = f"Bearer {self.access_tokens[email]}"
                            continue
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(email, proxy, Fore.RED, f"Lấy danh sách nhiệm vụ thất bại: {Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}")

        return None

    async def complete_task(self, email: str, task_field: str, use_proxy: bool, rotate_proxy: bool, proxy=None, retries=5):
        url = f"{self.BASE_API}/users/task"
        data = json.dumps({"email":email, "field":task_field})
        headers = self.HEADERS[email].copy()
        headers["Authorization"] = f"Bearer {self.access_tokens[email]}"
        headers["Content-Length"] = str(len(data))
        headers["Content-Type"] = "application/json"
        for attempt in range(retries):
            connector = ProxyConnector.from_url(proxy) if proxy else None
            try:
                async with ClientSession(connector=connector, timeout=ClientTimeout(total=60)) as session:
                    async with session.patch(url=url, headers=headers, data=data, ssl=False) as response:
                        if response.status == 401:
                            self.print_message(email, proxy, Fore.YELLOW, "Token hết hạn, đang thử đăng nhập lại.")
                            await self.process_user_login(email, use_proxy, rotate_proxy)
                            headers["Authorization"] = f"Bearer {self.access_tokens[email]}"
                            continue
                        response.raise_for_status()
                        return await response.json()
            except (Exception, ClientResponseError) as e:
                if attempt < retries - 1:
                    await asyncio.sleep(5)
                    continue
                self.print_message(email, proxy, Fore.WHITE, f"Nhiệm vụ {task_field}{Fore.RED+Style.BRIGHT} chưa hoàn thành: {Fore.YELLOW+Style.BRIGHT}{str(e)}{Style.RESET_ALL}")

        return None

    async def process_check_connection(self, email: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None

            check = await self.check_connection(email, proxy)
            if check and check.get("status") == "success":
                return True

            if rotate_proxy:
                proxy = self.rotate_proxy_for_account(email)

            await asyncio.sleep(5)

    async def process_user_login(self, email: str, use_proxy: bool, rotate_proxy: bool):
        return await self.user_login(email, None)

    async def looping_user_login(self, email: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            await asyncio.sleep(24 * 60 * 55)
            await self.user_login(email, None)

    async def looping_perform_checkin(self, email: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None

            users = await self.user_info(email, use_proxy, rotate_proxy, proxy)
            if users:
                checked_in = users["checkedIn"]

                if checked_in:
                    self.print_message(email, proxy, Fore.YELLOW, "Đã check-in hôm nay")
                else:
                    checkin = await self.perform_checkin(email, use_proxy, rotate_proxy, proxy)
                    if checkin:
                        self.print_message(email, proxy, Fore.GREEN, "Check-In thành công")

            await asyncio.sleep(12 * 60 * 60)

    async def process_connect_node(self, email: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None

            connect = await self.connect_node(email, use_proxy, rotate_proxy, proxy)
            if connect and connect.get("message") == "Last active time updated":
                self.print_message(email, proxy, Fore.GREEN, "Lite Node đã kết nối")
                return True

            await asyncio.sleep(5)

    async def looping_connect_node(self, email: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            await self.process_connect_node(email, use_proxy, rotate_proxy)
            await asyncio.sleep(24 * 60 * 60)

    async def looping_update_point(self, email: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None

            update = await self.update_point(email, use_proxy, rotate_proxy, proxy)
            if update:
                point_today = update["pointsFarmToday"]
                point_total = update["totalPointsReceived"]
                today_uptime = update["todayUptime"]
                total_uptime = update["totalUptime"]

                self.print_message(email, proxy, Fore.GREEN, "Đã cập nhật điểm"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT}Thu nhập:{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} Hôm nay {point_today:.3f} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT} Tổng {point_total:.3f} {Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT}-{Style.RESET_ALL}"
                    f"{Fore.CYAN + Style.BRIGHT} Thời gian hoạt động: {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}Hôm nay {today_uptime}{Style.RESET_ALL}"
                    f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                    f"{Fore.WHITE + Style.BRIGHT}Tổng {total_uptime}{Style.RESET_ALL}"
                )

            await asyncio.sleep(90)

    async def looping_complete_tasks(self, email: str, use_proxy: bool, rotate_proxy: bool):
        while True:
            proxy = self.get_next_proxy_for_account(email) if use_proxy else None

            task_lists = await self.task_lists(email, use_proxy, rotate_proxy, proxy)
            if task_lists:
                tasks = [
                    (key, value) for key, value in task_lists.items()
                    if key not in ['_id', 'email', '__v']
                ]

                for task_filed, status in tasks:
                    if status is True:
                        continue

                    complete = await self.complete_task(email, task_filed, use_proxy, rotate_proxy, proxy)
                    if complete:
                        self.print_message(email, proxy, Fore.WHITE, f"Nhiệm vụ {task_filed} "
                            f"{Fore.GREEN + Style.BRIGHT}đã hoàn thành{Style.RESET_ALL}"
                        )

                    await asyncio.sleep(1)

                self.print_message(email, proxy, Fore.GREEN, "Đã xử lý tất cả nhiệm vụ khả dụng")

            await asyncio.sleep(24 * 60 * 60)                

    async def process_accounts(self, email: str, use_proxy: bool, rotate_proxy: bool):
        logined = await self.process_user_login(email, use_proxy, rotate_proxy)
        if logined:
            tasks = [
                asyncio.create_task(self.looping_user_login(email, use_proxy, rotate_proxy)),
                asyncio.create_task(self.looping_perform_checkin(email, use_proxy, rotate_proxy)),
                asyncio.create_task(self.looping_connect_node(email, use_proxy, rotate_proxy)),
                asyncio.create_task(self.looping_update_point(email, use_proxy, rotate_proxy)),
                asyncio.create_task(self.looping_complete_tasks(email, use_proxy, rotate_proxy))
            ]
            await asyncio.gather(*tasks)

    async def main(self):
        try:
            accounts = self.load_accounts()
            if not accounts:
                self.log(f"{Fore.RED + Style.BRIGHT}Không tải được tài khoản nào.{Style.RESET_ALL}")
                return

            use_proxy_choice, rotate_proxy = self.print_question()

            use_proxy = False
            if use_proxy_choice in [1, 2]:
                use_proxy = True

            self.clear_terminal()
            self.welcome()
            self.log(
                f"{Fore.GREEN + Style.BRIGHT}Tổng số tài khoản: {Style.RESET_ALL}"
                f"{Fore.WHITE + Style.BRIGHT}{len(accounts)}{Style.RESET_ALL}"
            )

            if use_proxy:
                await self.load_proxies(use_proxy_choice)

            self.log(f"{Fore.CYAN + Style.BRIGHT}={Style.RESET_ALL}"*75)

            tasks = []
            for idx, account in enumerate(accounts, start=1):
                if account:
                    email = account["Email"]
                    password = account["Password"]

                    if not "@" in email or not password:
                        self.log(
                            f"{Fore.CYAN + Style.BRIGHT}[ Tài khoản: {Style.RESET_ALL}"
                            f"{Fore.WHITE + Style.BRIGHT}{idx}{Style.RESET_ALL}"
                            f"{Fore.MAGENTA + Style.BRIGHT} - {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}Trạng thái:{Style.RESET_ALL}"
                            f"{Fore.RED + Style.BRIGHT} Dữ liệu tài khoản không hợp lệ {Style.RESET_ALL}"
                            f"{Fore.CYAN + Style.BRIGHT}]{Style.RESET_ALL}"
                        )
                        continue

                    self.HEADERS[email] = HEADERS
                    self.password[email] = password

                    tasks.append(asyncio.create_task(self.process_accounts(email, use_proxy, rotate_proxy)))

            await asyncio.gather(*tasks)

        except Exception as e:
            self.log(f"{Fore.RED+Style.BRIGHT}Lỗi: {e}{Style.RESET_ALL}")
            raise e

if __name__ == "__main__":
    try:
        bot = Monami()
        asyncio.run(bot.main())
    except KeyboardInterrupt:
        print(
            f"{Fore.CYAN + Style.BRIGHT}[ {datetime.now().astimezone(wib).strftime('%x %X %Z')} ]{Style.RESET_ALL}"
            f"{Fore.WHITE + Style.BRIGHT} | {Style.RESET_ALL}"
            f"{Fore.RED + Style.BRIGHT}[ THOÁT ] Monami Network - BOT{Style.RESET_ALL}"                                      
        )