class Page:
    def __init__(self, test):
        self.test = test
        self.base_url = test.live_server_url

        if hasattr(self, 'path'):
            self.url = self.base_url + self.path

        # Helper find element methods to reduce line lengths
        self.browser = test.browser
        self.BY_CLASS = test.browser.find_element_by_class_name
        self.BY_CSS = test.browser.find_element_by_css_selector
        self.BYS_CSS = test.browser.find_elements_by_css_selector
        self.BY_ID = test.browser.find_element_by_id
        self.BY_TAG = test.browser.find_element_by_tag_name
        self.BYS_TAG = test.browser.find_elements_by_tag_name
        self.BY_XPATH = test.browser.find_element_by_xpath

    def is_on_page(self):
        """Returns True if the browser is currently on this page"""
        if hasattr(self, 'path'):
            return self.test.get_url_path() == self.path
        else:
            raise NotImplementedError('You need to specify the page path.')

    def go_to(self):
        """Instructs the browser to go to this page object's URL"""
        if hasattr(self, 'url'):
            self.browser.get(self.url)
            return self
        else:
            raise NotImplementedError('You need to specify the page path.')

    def go_to_and_check_on_page(self):
        self.go_to()
        assert self.is_on_page()
