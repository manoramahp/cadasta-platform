from .base import Page


class ProjectPage(Page):

    def __init__(self, test, org_slug, project_slug):
        self.path = '/organizations/{}/projects/{}/'.format(
            org_slug, project_slug)
        super().__init__(test)

    def get_org_name(self):
        return self.BY_CSS('.org-name').text

    def get_project_name(self):
        project_name = self.test.page_title().text
        project_name = project_name.replace(self.get_org_name(), '')
        project_name = project_name.replace('\n', '')
        return project_name

    def get_project_description(self):
        return self.BY_CSS('.detail p').text

    def check_page_contents(self, target_project):
        """This checks that the page displays the correct project data
        based on the supplied test data for a project."""

        assert self.get_org_name() == target_project['_org_name']
        assert self.get_project_name() == target_project['name'].upper()
        assert self.get_project_description() == target_project['description']
