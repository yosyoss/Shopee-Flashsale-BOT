import json
import os
import tempfile
import time
import traceback

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException
from colorama import Fore, Style
from progress.spinner import MoonSpinner

from lib.moduleChecker import clearConsole


# Class names / text patterns that indicate the user is logged in to Shopee.
# Shopee rotates these periodically; we check several to be robust.
LOGIN_INDICATORS = (
    'navbar__user-avatar',
    'navbar__user-portrait',
    'navbar__username',
    'shopee-avatar',
    'class="user-sidebar"',
    'Akun Saya',
    'My Account',
    # Cart count is only shown to logged-in users
    'class="shopee-cart-drawer"',
    'shopee-cart-icon',
    'cart-drawer-container',
    # Common logged-in indicators in page source
    'Logout',
    'Keluar',
    'user-portrait',
    # Specific to Yosua's account (won't match for other users but harmless)
    'yosua',
)


def _wait_for_page(driver, predicate, message, timeout_seconds=300, poll_interval=1.0):
    """Poll driver.page_source until predicate(html) returns True.

    Polls every `poll_interval` seconds (so we don't hammer the browser),
    catches transient WebDriverException (network glitches, page reloads),
    and exits cleanly on KeyboardInterrupt. Returns (matched, elapsed).
    """
    spinner = MoonSpinner(Fore.LIGHTYELLOW_EX + message)
    start = time.time()
    try:
        while True:
            try:
                htmlsource = driver.page_source
            except WebDriverException:
                time.sleep(poll_interval)
                spinner.next()
                continue
            if predicate(htmlsource):
                spinner.finish()
                return True, time.time() - start
            elapsed = time.time() - start
            if elapsed >= timeout_seconds:
                spinner.finish()
                return False, elapsed
            time.sleep(poll_interval)
            spinner.next()
    except KeyboardInterrupt:
        spinner.finish()
        return False, time.time() - start


def _check_logged_in(html, url=''):
    """Detect if user is logged in to Shopee.

    Checks the page source for typical logged-in indicators AND
    the URL parameter `is_logged_in=true` which Shopee includes
    on its anti-bot pages when cookies are valid.
    """
    if 'is_logged_in=true' in url:
        return True
    return any(ind in html for ind in LOGIN_INDICATORS)


def _check_flashsale_active(html):
    """Detect that the Shopee flash sale is active or about to start.

    Returns True if any of these markers is present in the page source.
    Markers are specific enough to avoid false positives on regular
    product pages.
    """
    markers = (
        'berakhir dalam',      # ends in (active sale)
        'ends in',             # English
        'dimulai dalam',       # starts in (upcoming sale)
        'starts in',
        'sedang berlangsung',  # currently ongoing
        'stok tersisa',        # stock remaining (only on flash sale)
    )
    html_lower = html.lower()
    return any(m in html_lower for m in markers)


def _check_checkout_button(html):
    return 'shopee-button-solid--primary' in html


def _connect_to_user_chrome(driverPath, platform, retries=4, delay=0.5):
    """Try to connect to user's existing Chrome via DevTools Protocol.

    Retries several times because Chrome may still be starting up after
    launch_chrome_debug.bat. Tries 127.0.0.1 (most common) and localhost
    as fallback. Returns a WebDriver on success, None otherwise.
    When connected, the bot inherits the user's cookies, login state,
    and browser fingerprint — Shopee sees a returning logged-in user
    and no captcha is triggered.
    """
    import requests
    debug_port = 9222
    # Chrome's DevTools server typically binds to 127.0.0.1 (IPv4) or localhost
    addresses = ['127.0.0.1', 'localhost']

    for attempt in range(1, retries + 1):
        for addr in addresses:
            try:
                url = f'http://{addr}:{debug_port}/json/version'
                r = requests.get(url, timeout=0.5)
                if r.status_code == 200:
                    log_path = '/dev/null' if platform == 'Linux' else 'NUL'
                    opts = webdriver.ChromeOptions()
                    opts.add_experimental_option('debuggerAddress', f'{addr}:{debug_port}')
                    service = Service(executable_path=driverPath, log_path=log_path)
                    driver = webdriver.Chrome(service=service, options=opts)
                    if attempt > 1 or addr != '127.0.0.1':
                        print(f'    (connected via {addr} after {attempt} attempts)', flush=True)
                    return driver
            except Exception:
                pass
        if attempt < retries:
            time.sleep(delay)

    return None


def _launch_headless_chrome_with_profile(driverPath, platform):
    """Launch headless Chrome via subprocess + attach via CDP.

    Why this approach: launching Chrome via Selenium's webdriver.Chrome()
    directly is unreliable on this system (intermittent "Chrome instance
    exited" / "DevToolsActivePort file doesn't exist" crashes). The reliable
    path is to launch Chrome with subprocess.Popen (so we control flags
    exactly), wait for the debug port to bind, then attach Selenium via
    Chrome DevTools Protocol (CDP).

    The user only needs to log in to Shopee ONCE in this portable Chrome
    via open_portable_chrome.bat; cookies persist in ./chrome-profile/.
    """
    import subprocess
    import requests

    # Close any existing Chrome instances
    print(Fore.CYAN + '    [ Closing any existing Chrome instances... ]', flush=True)
    subprocess.run(['taskkill', '/F', '/IM', 'chrome.exe', '/T'],
                   capture_output=True)
    print(Fore.CYAN + '    [ Waiting 8s for file locks to release... ]', flush=True)
    time.sleep(8)

    # Use the portable Chrome we extracted - this is the Chrome that the
    # user can see and interact with. Non-headless mode + portable Chrome
    # binary both avoid the user's enterprise Chrome policy issues, and
    # --remote-debugging-port binds successfully.
    #
    # IMPORTANT: launch to Shopee HOMEPAGE first, not the product URL.
    # Shopee's anti-bot is more aggressive on direct product links
    # (scene=crawler_item). The homepage is safer; we navigate to the
    # product URL after CDP attach, with a delay so it looks natural.
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    portable_chrome = os.path.join(
        project_root, 'chrome-portable', 'chrome-win64', 'chrome.exe')
    bot_profile = os.path.join(project_root, 'chrome-profile')

    debug_port = 9222
    args = [
        portable_chrome,
        # NO --headless! User wants to see and interact with the browser.
        '--disable-gpu',
        '--no-sandbox',
        '--disable-dev-shm-usage',
        '--no-first-run',
        '--no-default-browser-check',
        f'--user-data-dir={bot_profile}',
        f'--remote-debugging-port={debug_port}',
        '--remote-allow-origins=*',
        '--start-maximized',
        'https://shopee.co.id',  # Homepage first (anti-bot safer)
    ]

    print(Fore.CYAN + '    [ Launching Chrome portable via subprocess... ]', flush=True)
    proc = subprocess.Popen(
        args,
        creationflags=getattr(subprocess, 'CREATE_NEW_PROCESS_GROUP', 0),
    )
    print(f'    [ Chrome PID: {proc.pid} ]', flush=True)

    # Wait for debug port to bind (up to 20s)
    print(Fore.CYAN + f'    [ Waiting for Chrome debug port {debug_port}... ]', flush=True)
    for i in range(20):
        try:
            r = requests.get(f'http://127.0.0.1:{debug_port}/json/version', timeout=1)
            if r.status_code == 200:
                print(Fore.GREEN +
                      f'    [ ✔ Debug port ready after {i+1}s ]', flush=True)
                break
        except Exception:
            time.sleep(1)
    else:
        proc.terminate()
        raise RuntimeError(f'Chrome debug port {debug_port} did not bind within 20s')

    # Attach Selenium to the running Chrome via CDP
    log_path = '/dev/null' if platform == 'Linux' else 'NUL'
    abs_driver_path = os.path.abspath(driverPath)
    opts = webdriver.ChromeOptions()
    opts.add_experimental_option('debuggerAddress', f'127.0.0.1:{debug_port}')
    service = Service(executable_path=abs_driver_path, log_path=log_path)
    print(Fore.CYAN + '    [ Attaching Selenium via CDP... ]', flush=True)
    return webdriver.Chrome(service=service, options=opts)


def executeScript(**params):
    url = params['url']
    driverPath = params['chromedriver']
    platform = params['platform']

    # Step 1: try to connect to user's already-running Chrome.
    # If the user launched Chrome with --remote-debugging-port=9222,
    # we attach to it and inherit their login + fingerprint (no captcha).
    log_path = '/dev/null' if platform == 'Linux' else 'NUL'
    service = Service(executable_path=driverPath, log_path=log_path)

    print(Fore.CYAN + '  [ Checking if Chrome is open with debug port (9222)... ]')
    driver = _connect_to_user_chrome(driverPath, platform)
    if driver is not None:
        print(Fore.GREEN +
              '  [ ✔ Connected to your existing Chrome — using your logged-in session ]\n')
    else:
        # Fallback: launch our own headless Chrome with the user's profile.
        # This is the only config that works on this system: headless + user's
        # real profile = debug port binds + cookies/login auto-applied.
        print(Fore.YELLOW +
              '  [ No Chrome with debug port detected — launching one in headless mode... ]\n'
              '  [ Using your existing Chrome profile (cookies/login preserved). ]\n'
              '  [ This will close any open Chrome windows first. ]\n')
        try:
            driver = _launch_headless_chrome_with_profile(driverPath, platform)
            print(Fore.GREEN +
                  '  [ ✔ Headless Chrome started with your logged-in session ]\n')
        except WebDriverException as e:
            print(Fore.RED + f'\n[ Failed to start Chrome: {e} ]\n')
            return

    # Open the target URL directly. No auto-login via session cookies —
    # those trip Shopee's anti-bot (captcha). User logs in manually.
    try:
        driver.get(url)
    except WebDriverException as e:
        print(Fore.RED + f'\n[ Failed to open URL: {e} ]\n')
        try:
            driver.quit()
        except Exception:
            pass
        return

    clearConsole()
    print(Fore.GREEN + '  [ ✔ Browser window opened (you should see Chrome now) ]\n')
    print(Fore.CYAN + '  [ Please navigate to the flashsale URL MANUALLY in Chrome: ]\n')
    print(Fore.CYAN + f'  [   {url} ]\n')
    print(Fore.CYAN + '  [ Direct navigation by bot triggers Shopee captcha. ]\n')
    print(Fore.CYAN + '  [ Manual navigation looks human and avoids the captcha. ]\n')
    print(Fore.CYAN + '  [ When on the product page, the bot will start monitoring. ]\n')
    print(Fore.CYAN + '  [ While on the page, also: select the variant (color/size) ]\n')

    # Wait for user to manually navigate to the product URL.
    # The product URL pattern is 'shopee.co.id/...-i.<shop_id>.<item_id>'
    # i.e. contains '-i.' followed by numbers.
    product_url_marker = url.split('/')[-1]  # the slug at end of URL
    print(Fore.CYAN +
          f'  [ Bot will detect when you visit: ...{product_url_marker[:40]}... ]\n', flush=True)

    spinner = MoonSpinner(Fore.LIGHTYELLOW_EX +
                          'Waiting for you to navigate to the product page... ')
    start = time.time()
    try:
        while True:
            # Manual shortcut: user presses Enter in terminal to skip waiting
            try:
                import msvcrt
                if msvcrt.kbhit():
                    key = msvcrt.getwch()
                    if key in ('\r', '\n', ' '):
                        spinner.finish()
                        print(Fore.GREEN +
                              '\n  [ ⚡ Manual skip - assuming on product page ]\n')
                        break
            except ImportError:
                pass

            try:
                current = driver.current_url
                # Also force a page_source query to make Selenium re-sync with Chrome
                src = driver.page_source[:5000]
            except WebDriverException:
                time.sleep(1)
                spinner.next()
                continue
            # Match if the product slug is in the current URL or page source
            in_url = product_url_marker and product_url_marker[:30] in current and 'verify' not in current
            in_src = product_url_marker and product_url_marker[:30] in src
            if in_url or in_src:
                spinner.finish()
                print(Fore.GREEN + '\n  [ ✔ You are on the product page! ]\n')
                break
            elapsed = time.time() - start
            if elapsed > 900:  # 15 min timeout
                spinner.finish()
                print(Fore.YELLOW + '\n  [ Timeout waiting for product page ]\n')
                try:
                    driver.quit()
                except Exception:
                    pass
                input(Fore.GREEN + '[ Press Enter to exit ]' + Style.RESET_ALL)
                return
            time.sleep(1)
            spinner.next()
    except KeyboardInterrupt:
        spinner.finish()
        print(Fore.YELLOW + '\n  [ Interrupted ]\n')
        return

    # Now check if user is logged in
    matched, elapsed = _wait_for_page(
        driver,
        lambda h: _check_logged_in(h, driver.current_url),
        'Waiting for you to log in to Shopee (solve captcha if asked)...',
        timeout_seconds=600,
        poll_interval=1.0,
    )
    if not matched:
        print(Fore.YELLOW +
              f'\n  [ Login not detected after {int(elapsed)}s ]\n'
              '  [ Make sure you are fully logged in (username visible in navbar) ]\n'
              '  [ If captcha is blocking, complete it in the browser, then run again ]\n')
        try:
            driver.quit()
        except Exception:
            pass
        input(Fore.GREEN + '[ Press Enter to exit ]' + Style.RESET_ALL)
        return
    print(Fore.GREEN + f'\n  [ ✔ Logged in ({int(elapsed)}s) ]\n')
    print(Fore.CYAN + '  Select variant (color/size) on the page, then waiting for flash sale...\n')

    # Wait for flash sale timer to appear on the page, OR for user to
    # press Enter in the terminal (manual GO trigger).
    print(Fore.CYAN + '  [ Waiting for flash sale... ]\n'
          '  [ Select variant on the page, then either: ]\n'
          '  [   - Wait for Shopee timer to trigger the bot, OR ]\n'
          '  [   - Press Enter in THIS terminal to GO NOW (force click) ]\n', flush=True)

    poll_interval = 0.5
    start = time.time()
    spinner = MoonSpinner(Fore.GREEN + 'Waiting For FlashSale.. Press Enter to GO NOW ')
    try:
        while True:
            # Manual GO trigger: user pressed Enter in terminal
            import select
            import sys
            # On Windows, select() doesn't work on stdin. Use msvcrt instead.
            try:
                import msvcrt
                if msvcrt.kbhit():
                    key = msvcrt.getwch()
                    if key in ('\r', '\n', ' ', 'q'):
                        spinner.finish()
                        print(Fore.GREEN +
                              '\n  [ ⚡ Manual GO triggered! Clicking Buy NOW... ]\n')
                        break
            except ImportError:
                pass

            try:
                htmlsource = driver.page_source
            except WebDriverException:
                time.sleep(poll_interval)
                spinner.next()
                continue
            if _check_flashsale_active(htmlsource):
                spinner.finish()
                print(Fore.BLUE + '\n  [ ⚡ Flash sale detected! Clicking Buy NOW... ]\n')
                break
            elapsed = time.time() - start
            if elapsed > 1800:  # 30 min timeout
                spinner.finish()
                print(Fore.YELLOW +
                      f'\n  [ Flash sale timer not detected after {int(elapsed)}s ]\n')
                try:
                    driver.quit()
                except Exception:
                    pass
                input(Fore.GREEN + '[ Press Enter to exit ]' + Style.RESET_ALL)
                return
            time.sleep(poll_interval)
            spinner.next()
    except KeyboardInterrupt:
        spinner.finish()
        print(Fore.YELLOW + '\n  [ Interrupted by user ]\n')
        try:
            driver.quit()
        except Exception:
            pass
        return

    # Click "Beli Sekarang" / "Add to cart" then optionally checkout
    # Modern Shopee uses different class names. Try multiple selectors
    # in case Shopee changes the markup.
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.common.exceptions import TimeoutException, NoSuchElementException

    try:
        # Try multiple button selectors, prefer "Beli Sekarang" (Buy Now)
        # which goes directly to checkout - critical for flash sale race
        buy_selectors = [
            # Modern Shopee - Buy Now button (preferred for flash sale)
            'button[class*="btn-solid-primary"][class*="btn--l"]',
            'button.btn-solid-primary.btn--l',
            # Add to cart
            'button[class*="btn-tinted"][class*="btn--l"]',
            'button.btn-tinted.btn--l',
            # By text content
            'button:has-text("Beli Sekarang")',
            'button:has-text("Beli")',
            # Legacy selector (very old Shopee)
            'button.btn.btn-solid-primary.btn--l.rvHxix',
        ]

        buy_button = None
        used_selector = None
        for selector in buy_selectors:
            try:
                # Wait up to 5s for the button to be clickable
                wait = WebDriverWait(driver, 5)
                if ':has-text' in selector:
                    # XPath-style for text match
                    text = selector.split('"')[1]
                    xpath = f'//button[contains(text(), "{text}")]'
                    buy_button = wait.until(EC.element_to_be_clickable((By.XPATH, xpath)))
                else:
                    buy_button = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                used_selector = selector
                break
            except (TimeoutException, NoSuchElementException):
                continue

        if buy_button is None:
            raise RuntimeError(
                'Could not find Buy button. Shopee may have changed their markup. '
                'Please click "Beli Sekarang" manually in the browser.')

        # Scroll into view and click
        driver.execute_script(
            "arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});",
            buy_button)
        time.sleep(0.3)
        buy_button.click()
        print(Fore.LIGHTYELLOW_EX +
              f'\n  [ ✔ Buy button clicked (selector: {used_selector[:50]}...) ]\n')

        if not params.get('autoCheckout', True):
            return

        # Wait for cart page to load. Do NOT refresh - refreshing
        # unchecks the cart items and triggers the "no products selected"
        # modal. The cart is already loaded after Buy click.
        time.sleep(3)

        # Step 1: Check the item checkbox in cart. Shopee requires items
        # to be checked before Checkout button activates. The user might
        # have not checked the box, or the page may need re-confirmation.
        print(Fore.CYAN + '  [ Checking cart item checkbox... ]', flush=True)
        try:
            # Find the checkbox for the item we just added. Modern Shopee
            # uses a custom-styled div/label rather than a native input.
            # Try multiple selectors.
            checkbox_selectors = [
                # Modern Shopee: cart item checkbox (custom)
                '.cart-item .shopee-checkbox__input',
                '.cart-item input[type="checkbox"]',
                'input.shopee-checkbox__input',
                # Try clicking the label/box directly
                '.cart-item .shopee-checkbox',
                # Generic
                'div[class*="cart-item"] input',
            ]
            for selector in checkbox_selectors:
                try:
                    checkbox = WebDriverWait(driver, 3).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                    # Check if already checked
                    is_checked = checkbox.is_selected() if hasattr(checkbox, 'is_selected') else False
                    if not is_checked:
                        checkbox.click()
                        time.sleep(0.5)
                        print(Fore.GREEN + f'  [ ✔ Cart item checked ]', flush=True)
                    else:
                        print(Fore.CYAN + f'  [ Cart item already checked ]', flush=True)
                    break
                except (TimeoutException, NoSuchElementException):
                    continue
        except Exception as e:
            print(Fore.YELLOW + f'  [ Could not check cart item: {e} ]', flush=True)

        # Find the orange Checkout button at the bottom of the cart
        checkout_selectors = [
            'button[class*="shopee-button-solid--primary"][class*="checkout-btn"]',
            'button.shopee-button-solid.shopee-button-solid--primary',
            'button[class*="checkout"]',
            'button:has-text("Checkout")',
            'button:has-text("checkout")',
        ]

        checkout_button = None
        used_checkout_selector = None
        for selector in checkout_selectors:
            try:
                wait = WebDriverWait(driver, 5)
                if ':has-text' in selector:
                    text = selector.split('"')[1]
                    xpath = f'//button[contains(translate(text(), "ABCDEFGHIJKLMNOPQRSTUVWXYZ", "abcdefghijklmnopqrstuvwxyz"), "{text.lower()}")]'
                    checkout_button = wait.until(
                        EC.element_to_be_clickable((By.XPATH, xpath)))
                else:
                    checkout_button = wait.until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                used_checkout_selector = selector
                break
            except (TimeoutException, NoSuchElementException):
                continue

        if checkout_button is None:
            print(Fore.YELLOW +
                  '\n  [ Checkout button not found in cart page ]\n'
                  '  [ Please click "Checkout" MANUALLY in Chrome ]\n')
        else:
            # Scroll into view and click
            driver.execute_script(
                "arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});",
                checkout_button)
            time.sleep(0.5)
            try:
                checkout_button.click()
                print(Fore.BLUE +
                      f'\n  [ ✔ Checkout clicked (selector: {used_checkout_selector[:50]}...) ]\n')
            except WebDriverException as e:
                print(Fore.RED + f'\n  [ Checkout click failed: {e} ]\n')

        # Wait for order creation page (URL usually contains /checkout or /pay)
        # Look for "Buat Pesanan" button on the order page
        time.sleep(3)
        order_selectors = [
            'button:has-text("Buat Pesanan")',
            'button:has-text("Buat Pesanan Sekarang")',
            'button[class*="checkout-btn"]',
        ]
        for selector in order_selectors:
            try:
                if ':has-text' in selector:
                    text = selector.split('"')[1]
                    xpath = f'//button[contains(text(), "{text}")]'
                    order_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.XPATH, xpath)))
                else:
                    order_btn = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable((By.CSS_SELECTOR, selector)))
                driver.execute_script(
                    "arguments[0].scrollIntoView({behavior: 'instant', block: 'center'});",
                    order_btn)
                time.sleep(0.3)
                order_btn.click()
                print(Fore.GREEN +
                      '\n  [ ✔ "Buat Pesanan" clicked - order placed! ]\n')
                break
            except (TimeoutException, NoSuchElementException):
                continue
        else:
            print(Fore.YELLOW +
                  '\n  [ Could not auto-click "Buat Pesanan" ]\n'
                  '  [ Please click it MANUALLY in Chrome to complete order ]\n')

    except KeyboardInterrupt:
        print(Fore.YELLOW + '\n  [ Interrupted by user ]\n')
    except WebDriverException as e:
        print(Fore.RED + f'\n  [ Browser disconnected: {str(e)[:100]} ]\n')
    except Exception as e:
        print(Fore.RED + '\n  [ Error - item may be sold out or selectors changed ]\n')
        print(traceback.format_exc())
    finally:
        try:
            driver.quit()
        except Exception:
            pass

    input(Fore.GREEN + '[ Press Enter to exit ]' + Style.RESET_ALL)
    print(Fore.WHITE + '\nBye 👋' + Style.RESET_ALL)
