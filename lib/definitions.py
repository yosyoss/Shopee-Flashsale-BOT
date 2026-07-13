import collections
import time
import inquirer
import json
import os
import platform
import wget

from requests import get, post
from colorama import Fore, Style
from zipfile import ZipFile
from lib.driverExecutor import executeScript

def initProgram():
    clearConsole()
    settings = readFileJson('./config/index.json')
    title = headerOutput(autoCheckout=settings['autoCheckout'], autoOrder=settings['autoOrder'], chromedriver=settings['chromedriver'],
                         session=settings['session'], urlTarget=settings['url'], options=settings['options'], justTitle=False)
    print(title)

def clearConsole():
    command = 'clear'
    if os.name in ('nt', 'dos'):  # If Machine is running on Windows, use cls
        command = 'cls'
    os.system(command)

def readDir(path):
    return os.listdir(path)

def readFileJson(file):
    f = open(file, 'r')
    data = json.loads(f.read())
    f.close()

    return data

def writeFileJson(obj, file):
    jsonObj = json.dumps(obj, indent=4)

    with open(file, "w") as outfile:
        outfile.write(jsonObj)


def headerOutput(autoCheckout, autoOrder, chromedriver, session, urlTarget, options=[], justTitle=True):
    string = f'''
{Fore.LIGHTBLACK_EX}==========================================================
#          {Fore.RED}Shopee Flashsale BOT {Fore.LIGHTBLACK_EX}- {Fore.WHITE}By YOS         {Fore.LIGHTBLACK_EX}#
# ====================================================== #
'''
    if not justTitle:
        string += f'''
{Fore.GREEN}Platform        :{Style.RESET_ALL} {(Fore.BLUE + platform.system() + Style.RESET_ALL)}
{Fore.GREEN}Session Name    :{Style.RESET_ALL} {(Fore.BLUE + session + Style.RESET_ALL) if session not in [None, ''] else (Fore.YELLOW + '[Select Session Account]' + Style.RESET_ALL)}
{Fore.GREEN}Shopee Item Url :{Style.RESET_ALL} {(Fore.BLUE + urlTarget + Style.RESET_ALL) if urlTarget not in [None, ''] else (Fore.YELLOW + '[Insert Flashsale Shopee URL]' + Style.RESET_ALL)}
{Fore.GREEN}Chromedriver    :{Style.RESET_ALL} {(Fore.BLUE + chromedriver + Style.RESET_ALL) if chromedriver not in [None, ''] else (Fore.YELLOW + '[Select Chromedriver]' + Style.RESET_ALL)}
{Fore.GREEN}Auto Checkout   :{Style.RESET_ALL} {'✔️' if autoCheckout else '❌'}
{Fore.GREEN}Auto Order      :{Style.RESET_ALL} {'✔️' if autoOrder else '❌'} {Fore.LIGHTRED_EX}[This Feature Will Added Soon]
'''
        if len(options) != 0:
            string += f'{Fore.LIGHTBLACK_EX}# ===================== [ Options ] ==================== #\n'
            for i in range(len(options)):
                string += f'''
{Fore.GREEN + options[i][0]} :{Style.RESET_ALL} {(Fore.BLUE + options[i][1] + Style.RESET_ALL) if options[i][1] not in [None, ''] else (Fore.YELLOW + '-' + Style.RESET_ALL)}'''

    return string


def getWebdriverList(webdriver = 'chrome'):
    if webdriver == 'chrome':
        # Chrome-for-Testing JSON endpoint (replaces deprecated chromedriver.storage.googleapis.com)
        chromeDriverUrl = 'https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json'
        fetchChromeDriver = get(chromeDriverUrl).json()
        webdriverList = {}
        for entry in fetchChromeDriver.get('versions', []):
            driverVersion = entry['version']
            downloads = entry.get('downloads', {})
            chromedriverDownloads = downloads.get('chromedriver', [])
            if not chromedriverDownloads:
                continue
            platformMap = {}
            for dl in chromedriverDownloads:
                platformKey = dl.get('platform')
                if platformKey in ('win32', 'linux64', 'mac-x64', 'mac-arm64'):
                    platformMap[platformKey] = dl.get('url')
            if platformMap:
                webdriverList[driverVersion] = platformMap
        webdriverList = collections.OrderedDict(sorted(webdriverList.items()))
        writeFileJson(webdriverList, './webdriver/chromedriver.json')
        return webdriverList
    if webdriver == 'firefox':
        return ['firefox']
    if webdriver =='safari':
        return ['safari']
    if webdriver == 'ie':
        return ['ie']


def _platformToChromePlatform(_platform, machine=''):
    """Map platform.system() output to Chrome-for-Testing platform key."""
    if _platform == 'Windows':
        return 'win32'
    if _platform == 'Linux':
        return 'linux64'
    if _platform == 'Darwin':
        # Apple Silicon (M1/M2) uses arm64
        if 'arm' in (machine or '').lower():
            return 'mac-arm64'
        return 'mac-x64'
    return None


def _downloadChromeDriver(version, driverURL):
    """Download and extract chromedriver zip, returning the path to the extracted binary."""
    zipName = driverURL.split('/')[-1]
    zipPath = './webdriver/' + zipName
    wget.download(driverURL, out=zipPath)
    with ZipFile(zipPath, 'r') as zip_ref:
        zip_ref.extractall(path='webdriver/')
    os.remove(zipPath)
    # Extracted folder is named like 'chromedriver-win32/' containing chromedriver.exe
    extracted_dir = './webdriver/' + zipName.replace('.zip', '')
    binary = os.path.join(extracted_dir, 'chromedriver.exe' if platform.system() == 'Windows' else 'chromedriver')
    return extracted_dir, binary


def _resolveDriverUrl(version, _platform, _machine, allVersions):
    chromePlatform = _platformToChromePlatform(_platform, _machine)
    if chromePlatform is None:
        raise RuntimeError(
            f'Unsupported platform: {_platform} ({_machine}) — cannot resolve ChromeDriver download URL.'
        )
    if version not in allVersions or chromePlatform not in allVersions[version]:
        raise RuntimeError(
            f'ChromeDriver v{version} not available for {chromePlatform}.'
        )
    return allVersions[version][chromePlatform]


def checkChromeDriver():
    settings = readFileJson('./config/index.json')
    chromeDriver = settings['chromedriver']
    chromeDir = readDir('./webdriver')
    _platform = platform.system()
    _machine = platform.machine()

    print('[🏁] Checking ChromeDriver...\n')
    time.sleep(1)
    print(f'{Fore.BLUE}Your platform is {_platform}')

    if chromeDriver.split('/')[-1] in chromeDir:
        print(f"{Fore.WHITE}{chromeDriver!r} installed ✔️")
        time.sleep(1)
        return

    print(
        f'{Style.RESET_ALL}Chromedriver is not detected, {Fore.YELLOW}Installing.. ⚠️\n')

    # Fetch the latest known-good version (single call, no user picker needed)
    print(f'{Fore.BLUE}Fetching latest known-good ChromeDriver version...')
    latestURL = 'https://googlechromelabs.github.io/chrome-for-testing/last-known-good-versions-with-downloads.json'
    latestData = get(latestURL).json()
    stableChannel = latestData.get('channels', {}).get('Stable', {})
    chosenVersion = stableChannel.get('version')
    if not chosenVersion:
        raise RuntimeError('Could not resolve latest ChromeDriver version from Chrome-for-Testing API.')

    print(f'{Fore.BLUE}Latest stable ChromeDriver: v{chosenVersion}')

    # Build URL from the latest endpoint
    downloads = stableChannel.get('downloads', {}).get('chromedriver', [])
    chromePlatform = _platformToChromePlatform(_platform, _machine)
    driverURL = None
    for dl in downloads:
        if dl.get('platform') == chromePlatform:
            driverURL = dl.get('url')
            break
    if driverURL is None:
        # Fallback: scan full version list
        print(f'{Fore.YELLOW}Latest endpoint did not include {chromePlatform}, scanning full version list...')
        allVersions = getWebdriverList()
        driverURL = _resolveDriverUrl(chosenVersion, _platform, _machine, allVersions)

    print(f'\n{Fore.BLUE}Downloading ChromeDriver {_platform} v{chosenVersion}{Fore.LIGHTRED_EX}\n')

    extracted_dir, binary_path = _downloadChromeDriver(chosenVersion, driverURL)

    # Move binary to ./webdriver/chromedriver[.exe] to match config expectation
    target = './webdriver/chromedriver' + ('.exe' if _platform == 'Windows' else '')
    if os.path.exists(target):
        os.remove(target)
    os.replace(binary_path, target)
    try:
        os.rmdir(extracted_dir)
    except OSError:
        pass  # leave folder if non-empty (LICENSE files etc.)

    print(Fore.WHITE + '\nInstalled ✔️')

    settings['chromedriver'] = target
    writeFileJson(settings, './config/index.json')

def menu():
    initProgram()

    selector = [
        '1. START COUNTDOWN',
        '2. OPTIONS',
        '3. RESET',
        '4. EXIT'

    ]
    list_menu = [
        inquirer.List(
            'main', message='Welcome to Shopee Flash Sale Bot, Select one menu..', choices=selector)
    ]

    _menu = inquirer.prompt(list_menu)
    choice = _menu['main']

    if '1' in choice:
        start_countdown()
    elif '2' in choice:
        menu_options()
    elif '3' in choice:
        reset_settings()
    elif '4' in choice:
        print(Fore.WHITE + 'See ya 👋' + Style.RESET_ALL)

def menu_options():
    initProgram()

    selector = [
        '2.1 Select session',
        '2.2 Set Shopee Flashsale URL',
        '2.3 Back To Menu'
    ]
    list_opt = [
        inquirer.List('opt', message='Options', choices=selector)
    ]

    _opt = inquirer.prompt(list_opt)
    choice = _opt['opt']

    if '2.1' in choice:
        select_session()
    elif '2.2' in choice:
        set_url()
    elif '2.3' in choice:
        menu()

def reset_settings():
    answer = inquirer.prompt(
        [inquirer.Confirm('check', message='Are you sure to reset settings?')])
    settings = readFileJson('./config/index.json')

    if answer['check']:
        settings['session'] = ''
        settings['url'] = ''
        writeFileJson(settings, './config/index.json')
        menu()
    else:
        menu()

def set_url():
    settings = readFileJson('./config/index.json')

    URL = [inquirer.Text('url', message='Insert Shopee Flashsale URL')]
    answer = inquirer.prompt(URL)['url']
    if answer is None:
        menu()
        return

    # Sanitize: strip whitespace and extract URL if user pasted a noisy string
    cleaned = answer.strip()
    import re as _re
    match = _re.search(r'https?://\S+', cleaned)
    if match:
        cleaned = match.group(0).rstrip('.,;)')

    if not cleaned.lower().startswith(('http://', 'https://')):
        clearConsole()
        print(Fore.LIGHTRED_EX +
              '[ Invalid URL. It must start with http:// or https:// ]\n\n')
        input(Fore.GREEN + '[ Back ]' + Style.RESET_ALL)
        menu()
        return

    settings['url'] = cleaned
    writeFileJson(settings, './config/index.json')
    menu()

def select_session():
    session = readDir('./sessions')
    settings = readFileJson('./config/index.json')

    session_selector = []
    for i in session:
        if '.json' in i:
            session_selector.append(i)

    if len(session_selector) == 0:
        clearConsole()
        print(Fore.LIGHTRED_EX +
              '[ There is no account session, see README.md for steps to add session ]\n\n')
        input(Fore.GREEN + '[Back]' + Style.RESET_ALL)
        menu()
    else:
        list_session = [
            inquirer.List(
                'session', message='Select your account session', choices=session_selector)
        ]

        _session = inquirer.prompt(list_session)
        choice = _session['session']

        settings['session'] = choice
        writeFileJson(settings, './config/index.json')

        menu()

def start_countdown():
    settings = readFileJson('./config/index.json')

    if not settings['url']:
        clearConsole()
        print(Fore.LIGHTRED_EX +
              '[ Please Insert Shopee Flashsale Item URL ]\n\n')
        input(Fore.GREEN + '[ Back ]' + Style.RESET_ALL)
        menu()
    else:
        url = settings['url']
        if not isinstance(url, str) or not url.lower().startswith(('http://', 'https://')):
            clearConsole()
            print(Fore.LIGHTRED_EX +
                  f'[ Invalid URL stored in config: {url!r} ]\n'
                  '[ Please re-enter the URL via OPTIONS > 2.2 ]\n\n')
            input(Fore.GREEN + '[ Back ]' + Style.RESET_ALL)
            menu()
            return
        settings['platform'] = platform.system()
        executeScript(**settings)


# print(headerOutput(chromedriver='', session='', urlTarget='', options=[], justTitle=False))
