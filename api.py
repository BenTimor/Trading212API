from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from time import sleep

from Trading212.utils import force_click, Panel, type_sleep, script_click_xpath, Mode

class Trading212:
    def __init__(self, username, password, panel, headless, mode, long_sleep, short_sleep, timeout):
        # Creating headless browser if required
        self.mode = mode
        self.long_sleep = long_sleep
        self.short_sleep = short_sleep
        self.timeout = timeout
        if headless:
            options = webdriver.FirefoxOptions()
            options.headless = True
            self.driver = webdriver.Firefox(firefox_options=options)
        else:
            self.driver = webdriver.Firefox()

        self.driver.get("https://www.trading212.com/en/login")  # Getting a website
        self.setup(username, password, panel)

    def switch_mode(self):
        button_id = "equitySwitchButton" if self.mode == Mode.Invest else "cfdSwitchButton"
        elem = WebDriverWait(self.driver, 20).until(expected_conditions.element_to_be_clickable((By.ID, button_id)))
        if "active" not in elem.get_attribute('class').split():
            elem.click()

    def switch_panel(self, panel):
        """
        Switching panel if needed
        :param panel: Selected Panel
        :return: If panel switched
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
        Creating the driver for the object
        :param invest: Switch to invest account
        :param username: The username / email for trading212
        :param password: The password
        :param panel: Practice / Real Money
        """
        # Entering username and password
        self.driver.find_element_by_id("username-real").send_keys(username)
        self.driver.find_element_by_id("pass-real").send_keys(password)
        # Login
        self.driver.find_element_by_class_name("button-login").click()
        # Waiting and opening the user menu to avoid messages
        elem = WebDriverWait(self.driver, 20).until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "account-menu-button")))
        force_click(elem)
        # Switching panel if needed
        if self.switch_panel(panel):
            elem = WebDriverWait(self.driver, 20).until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "account-menu-button")))
            force_click(elem)
        # Switch to Invest
        self.switch_mode()
        WebDriverWait(self.driver, 20).until(expected_conditions.invisibility_of_element((By.ID, "platform-loader")))
        elem = self.driver.find_element_by_class_name("account-menu-button")
        elem.click()

    def buy_stock(self, stock, amount):
        """
        Buying a stock
        :param stock: Stock
        :param amount: Amount
        """
        # It's just opening a stock and buying it
        self.open_stock_dialog(stock)
        self.buy(amount)
        sleep(self.long_sleep)

    def buy(self, amount):
        """
        Buying a stock
        :param amount: How much of the stock you want to buy (Literal amount, Not money amount)
        """
        # Finding amount input
        elem = self.driver.find_elements_by_xpath("//div[@class='visible-input']//input[contains(@id, 'uniqName')]")[0]
        elem.clear()
        # Entering keys slowly because Trading212 removes it if it's written too fast
        type_sleep(elem, str(amount), self.short_sleep)
        # Confirm Button
        if self.mode == Mode.Invest:
            sleep(self.long_sleep)
            self.driver.find_elements_by_xpath("//div[@class='custom-button review-order-button']")[0].click()
            WebDriverWait(self.driver, 20).until(
                expected_conditions.element_to_be_clickable((By.XPATH, "//div[@class='custom-button send-order-button']"))).click()
        else:
            self.driver.find_elements_by_xpath("//div[contains(@class,'confirm-button')]")[0].click()

    def open_stock_dialog(self, stock):
        """
        Opening stock buy/sell dialog
        :param invest: Invest more
        :param stock: Stock as it's written in the panel
        """
        # It may be one of two elements
        elem = self.driver.find_elements_by_xpath("//span[contains(@data-dojo-attach-event, 'onOpenDialogClick')]")
        try:
            elem[0].click()
        except:
            elem[1].click()
        # Search the stock
        elem = self.driver.find_element_by_xpath("//input[@placeholder=\"Instrument search\"]")
        self.driver.execute_script("arguments[0].setAttribute('maxlength',arguments[1])", elem, 100)
        elem.send_keys(stock)
        # Open its dialog with JS hax
        script_click_xpath(self.driver, f"//*[@id='list-results-instruments']//span[contains(@class, 'instrument-name') and .='{stock}']")
        if self.mode == Mode.Invest:
            script_click_xpath(self.driver, "//span[@data-tab='market-order']")
        sleep(self.long_sleep)

    def result(self, stock):
        """
        Returning the result of a current position
        :param stock: Stock
        :return: The result in float
        """
        return float(self.position_info(stock, "ppl"))

    def position_info(self, stock, info):
        """
        Getting a specific position info
        :param stock: Stock
        :param info: The CSS class of this information
        :return: The info
        """
        return self.driver.find_elements_by_xpath(
            f"//td[@class='name' and text()='{stock}']/following::td[contains(@class,'{info}')]"
        )[0].text

class Invest(Trading212):
    def __init__(self, username, password, panel=Panel.Practice, headless=True, long_sleep=0.5, short_sleep=0.1, timeout=30):
        super().__init__(username, password, panel, headless, Mode.Invest, long_sleep, short_sleep, timeout)

    def close_position(self, stock):
        """
        Closing a position
        :param stock: Stock
        """
        # God knows why selenium can't click it. So I'm using javascript hacks.
        # And yeah, I know this line is too long, I just don't know how and where to split it. I don't really develop JS.
        quantity = self.position_info(stock, "quantity")
        script_click_xpath(self.driver, f"//td[@class='name' and text()='{stock}']/following::div[@class='button-wrapper']/child::div[@class='sell-button']")
        elem = WebDriverWait(self.driver, 20).until(expected_conditions.visibility_of_element_located((By.XPATH,"//div[@class='visible-input']//input")))
        #elem = self.driver.find_elements_by_xpath("//div[@class='visible-input']//input")[0]
        elem.clear()
        type_sleep(elem, quantity, self.short_sleep)
        sleep(self.long_sleep)
        self.driver.find_element_by_xpath("//div[@class='custom-button review-order-button']").click()
        WebDriverWait(self.driver, 20).until(expected_conditions.element_to_be_clickable((By.XPATH, "//div[@class='custom-button send-order-button']"))).click()

    def buy(self, amount):
        super().buy(amount)

    def open_stock_dialog(self, stock):
        super().open_stock_dialog(stock)

class CFD(Trading212):
    def __init__(self, username, password, panel=Panel.Practice, headless=True, long_sleep=0.5, short_sleep=0.1, timeout=30):
        super().__init__(username, password, panel, headless, Mode.CFD, long_sleep, short_sleep, timeout)

    def sell_stock(self, stock, amount):
        """
        Buying a stock
        :param stock: Stock
        :param amount: Amount
        """
        # It's just opening a stock and selling it
        self.open_stock_dialog(stock)
        self.sell(amount)
        sleep(self.long_sleep)

    def sell(self, amount):
        """
        Buying a stock
        :param amount: How much of the stock you want to buy (Literal amount, Not money amount)
        """
        # Switching to sell
        self.driver.find_elements_by_xpath("//div[@data-dojo-attach-event='click: setDirectionSell']")[0].click()
        # From there on it's exactly like the buy
        self.buy(amount)

    def close_position(self, stock):
        """
        Closing a position
        :param stock: Stock
        """
        self.driver.find_elements_by_xpath(
            f"//td[@class='name' and text()='{stock}']/following::div[@class='close-icon svg-icon-holder']"
        )[0].click()