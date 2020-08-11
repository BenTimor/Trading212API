from selenium import webdriver
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.common.by import By
from time import sleep

from utils import force_click, Panel

class Trading212:
    class CFD:
        def __init__(self, username, password, panel=Panel.Practice, headless=True, sleep_time=0.5):
            self.driver = Trading212.CFD.setup(username, password, panel, headless)
            self.sleep_time = 0.5
            self.panel = panel

        def sell_stock(self, stock, amount):
            """
            Buying a stock
            :param stock: Stock
            :param amount: Amount
            """
            # It's just opening a stock and selling it
            self.open_stock_dialog(stock)
            self.sell(amount)
            sleep(self.sleep_time)

        def buy_stock(self, stock, amount):
            """
            Buying a stock
            :param stock: Stock
            :param amount: Amount
            """
            # It's just opening a stock and buying it
            self.open_stock_dialog(stock)
            self.buy(amount)
            sleep(self.sleep_time)

        def sell(self, amount, sleep_time=0.1):
            """
            Buying a stock
            :param amount: How much of the stock you want to buy (Literal amount, Not money amount)
            :param sleep_time: How much time do you want to wait between letters
            """
            # Switching to sell
            self.driver.find_elements_by_xpath("//div[@data-dojo-attach-event='click: setDirectionSell']")[0].click()
            # From there on it's exactly like the buy
            self.buy(amount, sleep_time)

        def buy(self, amount, sleep_time=0.1):
            """
            Buying a stock
            :param amount: How much of the stock you want to buy (Literal amount, Not money amount)
            :param sleep_time: How much time do you want to wait between letters
            """
            # Finding amount input
            elem = self.driver.find_elements_by_xpath("//div[@class='visible-input']//input[contains(@id, 'uniqName')]")[0]
            elem.clear()
            # Entering keys slowly because Trading212 removes it if it's written too fast
            for a in str(amount):
                elem.send_keys(a)
                sleep(sleep_time)
            # Confirm Button
            self.driver.find_elements_by_xpath("//div[contains(@class,'confirm-button')]")[0].click()

        def open_stock_dialog(self, stock):
            """
            Opening stock buy/sell dialog
            :param stock: Stock as it's written in the panel
            """
            # It may be one of two elements
            elem = self.driver.find_elements_by_xpath("//span[contains(@data-dojo-attach-event, 'onOpenDialogClick')]")
            try:
                elem[0].click()
            except:
                elem[1].click()
            # Search the stock
            self.driver.find_element_by_xpath("//input[@placeholder=\"Instrument search\"]").send_keys(stock)
            # Open its dialog
            self.driver.find_element_by_xpath(f"//span[contains(text(),'{stock}')]").click()

        def close_position(self, stock):
            """
            Closing a position
            :param stock: Stock
            """
            self.driver.find_elements_by_xpath(
                f"//td[@class='name' and text()='{stock}']/following::div[@class='close-icon svg-icon-holder']"
            )[0].click()

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

        @staticmethod
        def switch_panel(driver, panel):
            """
            Switching panel if needed
            :param driver: Selenium Driver
            :param panel: Selected Panel
            :return: If panel switched
            """
            if panel == Panel.Practice:
                try:
                    elem = driver.find_element_by_class_name("green")
                    elem.click()
                except:
                    return False
            if panel == Panel.Real:
                try:
                    driver.find_element_by_class_name("green")
                    return False
                except:
                    elem = driver.find_element_by_class_name("blue")
                    elem.click()
            return True

        @staticmethod
        def setup(username, password, panel, headless):
            """
            Creating the driver for the object
            :param username: The username / email for trading212
            :param password: The password
            :param panel: Practice / Real Money
            :param headless: Headless is a browser without a GUI
            :return: Driver
            """
            # Creating headless browser if required
            if headless:
                options = webdriver.FirefoxOptions()
                options.headless = True
                driver = webdriver.Firefox(firefox_options=options)
            else:
                driver = webdriver.Firefox()
            driver.get("https://www.trading212.com/en/login")  # Getting a website
            # Entering username and password
            driver.find_element_by_id("username-real").send_keys(username)
            driver.find_element_by_id("pass-real").send_keys(password)
            # Login
            driver.find_element_by_class_name("button-login").click()
            # Waiting and opening the user menu to avoid messages
            elem = WebDriverWait(driver, 100).until(expected_conditions.element_to_be_clickable((By.CLASS_NAME, "account-menu-button")))
            force_click(elem)
            # Switching panel if needed
            if Trading212.CFD.switch_panel(driver, panel):
                elem = WebDriverWait(driver, 100).until(
                    expected_conditions.element_to_be_clickable((By.CLASS_NAME, "account-menu-button")))
                force_click(elem)
            # Clicking again to close menu
            elem.click()
            return driver
