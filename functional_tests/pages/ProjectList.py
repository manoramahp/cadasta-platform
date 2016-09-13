from selenium.common.exceptions import NoSuchElementException

from .base import Page
from django_countries import countries


class ProjectListPage(Page):
    path = '/projects/'

    def is_list_empty(self):
        cell = self.browser.find_element_by_xpath(
            "//table[@id='DataTables_Table_0']/tbody/tr/td"
        )
        return (cell.text == "No data available in table")

    def check_project_list(self, projects):
        """This verifies that the supplied list of projects
        and only these projects are visible on the page """

        rows = self.browser.find_elements_by_xpath(
            "//table[@id='DataTables_Table_0']/tbody/tr"
        )
        assert len(rows) == len(projects)
        for row in rows:
            onclick_items = row.get_attribute('onclick').split('/')
            project_slug = onclick_items[4]

            cells = row.find_elements_by_tag_name('td')
            actual_org_slug = onclick_items[2]
            try:
                img = cells[1].find_element_by_tag_name('img')
                actual_org_logo = img.get_attribute('src')
                actual_org_name = img.get_attribute('alt')
            except NoSuchElementException:
                actual_org_logo = None
                alt = cells[1].find_elements_by_class_name('org-name-alt')
                actual_org_name = alt[0].text
            actual_project_name = (
                cells[0].find_element_by_tag_name('h4').text
            )
            actual_project_description = (
                cells[0].find_element_by_tag_name('p').text
            )
            actual_country = cells[2].text

            target_project = None
            for project in projects:
                if project['slug'] == project_slug:
                    target_project = project
                    break
            assert target_project

            assert actual_org_slug == target_project['_org_slug']
            assert actual_org_name == target_project['_org_name']
            expected_org_logo = (
                target_project['_org_logo']
                if target_project['_org_logo']
                else None
            )
            assert actual_org_logo == expected_org_logo
            assert actual_project_name == target_project['name']
            assert actual_project_description == target_project['description']
            expected_country = (
                dict(countries)[target_project['country']]
                if target_project['country'] else ''
            )
            assert actual_country == expected_country

            # TODO Check also last updated column

    def follow_add_project_link(self):
        link = self.BY_CSS('.page-title a.btn-primary')
        link.click()
