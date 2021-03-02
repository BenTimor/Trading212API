from time import sleep

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from .utils import *


class Trading212:
    """
    Main API class
    """
    def __init__(self, username, password, panel, headless, mode, long_sleep, short_sleep, timeout):
        # Creating headless browser if required
        self.mode = mode
        self.long_sleep = long_sleep
        self.short_sleep = short_sleep
        self.timeout = timeout

        if headless:
            options = webdriver.FirefoxOptions()
            options.headless = True
            self.driver: webdriver.Firefox = webdriver.Firefox(firefox_options=options)
        else:
            self.driver: webdriver.Firefox = webdriver.Firefox()

        self.driver.get("https://www.trading212.com/en/login")  # Getting a website
        self.setup(username, password, panel)

    def switch_mode(self):
        """
        Switching the mode (Invest/CFD) if needed. The user menu has to be open so it'll work.
        """
        button_id = "equitySwitchButton" if self.mode == Mode.Invest else "cfdSwitchButton"
        elem = WebDriverWait(self.driver, self.timeout).until(expected_conditions.element_to_be_clickable((By.ID, button_id)))
        # If the button is active, you don't have to click on the button
        if "active" not in elem.get_attribute('class').split():
            elem.click()

    def switch_panel(self, panel):
        """
        Switching the panel (Practice/Real Money) if needed.The user menu has to be open so it'll work.
        :param panel: Selected Panel
        :return: If panel switched (Boolean)
        """
        if panel == Panel.Practice:
            try:
                elem = self.driver.find_element_by_class_name("green")
                elem.click()
            except:
                return False
        if panel == Panel.Real:
            try:
                self.driver.find_element_by_class_name("green")
                return False
            except:
                elem = self.driver.find_element_by_class_name("blue")
                elem.click()
        return True

    def setup(self, username, password, panel):
        """
        Creating the web drive.
        :param username: Login for trading212
        :param password: Password
        :param panel: Selected panel (Practice / Real Money)
        """
        # Entering username and password
        self.driver.find_element_by_id("username-real").send_keys(username)
        self.driver.find_element_by_id("pass-real").send_keys(password)
        # Login
        force_click(WebDriverWait(self.driver, self.timeout/2).until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "button-login"))))

        # Clicking on the button of the "YOUR ACCOUNT IS APPROVED!"
        try:
            elem = WebDriverWait(self.driver, self.timeout/2).until(expected_conditions.element_to_be_clickable((By.XPATH, "//div[@class='custom-button ']")))
            force_click(elem)
        except:
            pass

        # Navigate to the old app if the new app is opened by default
        try:
            elem = WebDriverWait(self.driver, self.timeout / 2).until(expected_conditions.element_to_be_clickable((By.XPATH, "//div[@class='account-menu-header']")))
            force_click(elem)
            
            elem = WebDriverWait(self.driver, self.timeout / 2).until(expected_conditions.element_to_be_clickable((By.XPATH, "//div[@class='account-menu-item switch-to-old']")))
            force_click(elem)
        except:
            pass

        # Waiting and opening the user menu to avoid the 'You're using CFD' message.
        elem = WebDriverWait(self.driver, self.timeout).until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "account-menu-button")))
        force_click(elem)
        # Switching panel if needed
        if self.switch_panel(panel):
            elem = WebDriverWait(self.driver, self.timeout).until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "account-menu-button")))
            force_click(elem)
        # Switching mode if needed.
        self.switch_mode()
        WebDriverWait(self.driver, self.timeout).until(expected_conditions.invisibility_of_element((By.ID, "platform-loader")))
        elem = self.driver.find_element_by_class_name("account-menu-button")
        elem.click()

    def buy_stock(self, stock, amount, method=BuyStockMethod.Shares):
        """
        Buying a stock
        :param stock: Stock (Display name)
        :param amount: It may be the amount of the shares and it may be the value of the money. It depends on your Trading212 defaults and I may fix it in the future. For now, You can debug it with headless=False parameter in the constructor.
        :param method: Shares - For buying the stock by its shares amount | Value - For buying the stock by its value
        """
        self.open_stock_dialog(stock)
        self.switch_buying_method(method)
        self.buy(amount)
        sleep(self.long_sleep)

    def buy(self, amount):
        """
        Buying the stock of the opened dialog
        :param amount: Amount
        """
        # Finding amount input
        elem = WebDriverWait(self.driver, self.timeout).until(expected_conditions.visibility_of_element_located((By.XPATH, "//div[@class='visible-input']//input[contains(@id, 'uniqName')]")))
        elem.clear()
        # Entering keys slowly because Trading212 removes it if it's written too fast
        type_sleep(elem, str(amount), self.short_sleep)
        # Confirm Button
        if self.mode == Mode.Invest:
            # The invest doesn't let you click on the button too fast
            sleep(self.long_sleep)
            self.driver.find_elements_by_xpath("//div[@class='custom-button review-order-button']")[0].click()
            WebDriverWait(self.driver, self.timeout).until(
                expected_conditions.element_to_be_clickable((By.XPATH, "//div[@class='custom-button send-order-button']"))).click()
        else:
            self.driver.find_elements_by_xpath("//div[contains(@class,'confirm-button')]")[0].click()

    def switch_buying_method(self, method):
        if self.mode == Mode.Invest:
            force_click(WebDriverWait(self.driver, self.timeout).until(expected_conditions.element_to_be_clickable((By.XPATH, "//div[@class='invest-by-content']"))))
            if method == BuyStockMethod.Value:
                # item item-invest-by-items-value
                # item item-invest-by-items-quantity
                self.driver.find_element_by_xpath("//div[@class='item item-invest-by-items-value']").click()
            else:
                self.driver.find_element_by_xpath("//div[@class='item item-invest-by-items-quantity']").click()


    def open_stock_dialog(self, stock):
        """
        Opening stock dialog
        :param stock: Stock (Display name)
        """
        # It may be one of two elements
        WebDriverWait(self.driver, self.timeout/2).until(expected_conditions.visibility_of_any_elements_located((By.XPATH, "//span[contains(@data-dojo-attach-event, 'onOpenDialogClick')]")))
        elem = self.driver.find_elements_by_xpath("//span[contains(@data-dojo-attach-event, 'onOpenDialogClick')]")
        try:
            elem[0].click()
        except:
            elem[1].click()
        # Search the stock
        elem = self.driver.find_element_by_xpath("//input[@placeholder=\"Instrument search\"]")
        # Setting the max length to 100 so the API'll be able to enter long stocks names
        self.driver.execute_script("arguments[0].setAttribute('maxlength',arguments[1])", elem, 100)
        elem.send_keys(stock)
        # Open its dialog with JS. Selenium couldn't open the dialog itself.
        script_click_xpath(self.driver, f"//*[@id='list-results-instruments']//span[contains(@class, 'instrument-name') and .='{stock}']")
        if self.mode == Mode.Invest:
            # Sometimes the invest opens the "Limit" tab instead of the "Market Order"
            script_click_xpath(self.driver, "//span[@data-tab='market-order']")
        sleep(self.long_sleep)

    def result(self, stock):
        """
        Returning a result of a position
        :param stock: Stock (Display name)
        :return: Result in float
        """
        return float(self.position_info(stock, "ppl"))

    def position_info(self, stock, info):
        """
        Getting a specific position 'info'
        :param stock: Stock (Display name)
        :param info: The CSS class of this information
        :return: The visual text
        """
        return self.driver.find_elements_by_xpath(
            f"//td[@class='name' and text()='{stock}']/following::td[contains(@class,'{info}')]"
        )[0].text
    
    def close(self):
        self.driver.close()

class Invest(Trading212):
    """
    Used for Invest mode interactions
    """
    def __init__(self, username, password, panel=Panel.Practice, headless=True, long_sleep=0.5, short_sleep=0.1, timeout=30):
        """
        :param username: Login
        :param password: Password
        :param panel: Practice / Real Money
        :param headless: Open GUI browser
        :param long_sleep: The animations of Trading212 require to wait a little sometimes.
        :param short_sleep: Waiting on 'slow' type.
        :param timeout: Timeout on waiting for elements
        """
        super().__init__(username, password, panel, headless, Mode.Invest, long_sleep, short_sleep, timeout)

    def close_position(self, stock):
        """
        Closing a position
        :param stock: Stock (Display name)
        """
        # God knows why selenium can't click it. So I'm using javascript hacks.
        quantity = self.position_info(stock, "quantity")
        script_click_xpath(self.driver, f"//td[@class='name' and text()='{stock}']/following::div[@class='button-wrapper']/child::div[@class='sell-button']")
        self.switch_buying_method(BuyStockMethod.Shares)
        elem = WebDriverWait(self.driver, self.timeout).until(expected_conditions.visibility_of_element_located((By.XPATH,"//div[@class='visible-input']//input")))
        elem.clear()
        type_sleep(elem, quantity, self.short_sleep)
        sleep(self.long_sleep)
        self.driver.find_element_by_xpath("//div[@class='custom-button review-order-button']").click()
        WebDriverWait(self.driver, self.timeout).until(expected_conditions.element_to_be_clickable((By.XPATH, "//div[@class='custom-button send-order-button']"))).click()

class CFD(Trading212):
    def __init__(self, username, password, panel=Panel.Practice, headless=True, long_sleep=0.5, short_sleep=0.1, timeout=30):
        super().__init__(username, password, panel, headless, Mode.CFD, long_sleep, short_sleep, timeout)

    def sell_stock(self, stock, amount):
        """
        Buying a stock
        :param stock: Stock (Display name)
        :param amount: Amount
        """
        # It's just opening a stock and selling it
        self.open_stock_dialog(stock)
        self.sell(amount)
        sleep(self.long_sleep)

    def sell(self, amount):
        """
        Shorting the stock of the opened dialog
        :param amount: Amount
        """
        # Switching to sell
        self.driver.find_elements_by_xpath("//div[@data-dojo-attach-event='click: setDirectionSell']")[0].click()
        # From there on it's exactly like the buy
        self.buy(amount)

    def close_position(self, stock):
        """
        Closing a position
        :param stock: Stock (Display name)
        """
        self.driver.find_elements_by_xpath(
            f"//td[@class='name' and text()='{stock}']/following::div[@class='close-icon svg-icon-holder']"
        )[0].click()
