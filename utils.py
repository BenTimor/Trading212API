from time import sleep

class Panel:
    """
    Allows you to select between practice and real
    """
    Practice = "Practice"
    Real = "Real"

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