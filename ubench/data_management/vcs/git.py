import os
import ubench.utils as utils


class Git:

    def __init__(self, repo_path):
        self.repo_path = repo_path

    def get_files_from_tag(self, tag):

        git_cmd = "git show {} --pretty=\"\" --name-only".format(tag)
        ret_code, files, stderr = utils.run_cmd(git_cmd, self.repo_path)
        return [os.path.join(self.repo_path,fl) for fl in files]
