from selenium.common.exceptions import NoSuchElementException

from .base import Page


class DashboardPage(Page):
    path = '/dashboard/'

    def get_dashboard_map(self):
        return self.browser.find_element_by_id('dashboard-map')

    def has_nav_link(self, title):
        try:
            return self.browser.find_element_by_xpath(
                '//nav'
            ).find_element_by_link_text(title)
        except NoSuchElementException:
            return None
