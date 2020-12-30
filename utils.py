from time import sleep


class Panel:
    """
    Allows you to select between practice and real
    """
    Practice = "Practice"
    Real = "Real"

class Mode:
    Invest = "Invest"
    CFD = "CFD"

class BuyStockMethod:
    Shares = "Shares"
    Value = "Value"

def force_click(element, sleep_time=1):
    """
    Clicks something until it works
    :param element: The element to click on
    :param sleep_time: How many time to wait between clicks
    """
    while True:
        try:
            element.click()
            return
        except:
            sleep(sleep_time)

def type_sleep(element, text, time):
    for t in text:
        element.send_keys(t)
        sleep(time)

def script_click_xpath(driver, xpath):
    driver.execute_script(f"document.evaluate(\"{xpath}\", document, null, XPathResult.FIRST_ORDERED_NODE_TYPE, null).singleNodeValue.click()")
