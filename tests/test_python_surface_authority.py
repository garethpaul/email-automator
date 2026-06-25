from __future__ import absolute_import

import os
import shutil
import subprocess
import sys
import tempfile
import unittest


ROOT_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
AUTHORITY_PATH = os.path.join(ROOT_DIR, "scripts", "verify-python-surface.py")
if sys.version_info[0] == 2:
    import imp
    AUTHORITY = imp.load_source("email_python_surface_authority", AUTHORITY_PATH)
else:
    import importlib.util
    AUTHORITY_SPEC = importlib.util.spec_from_file_location(
        "email_python_surface_authority", AUTHORITY_PATH
    )
    AUTHORITY = importlib.util.module_from_spec(AUTHORITY_SPEC)
    AUTHORITY_SPEC.loader.exec_module(AUTHORITY)


class PythonSurfaceAuthorityTest(unittest.TestCase):
    def executable_available(self, executable):
        if not executable or executable == "-":
            return False
        try:
            return subprocess.call(
                [executable, "-c", "import sys"],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
            ) == 0
        except OSError:
            return False

    def test_deployment_boundaries_are_derived_from_repository_layout(self):
        expected_role = AUTHORITY.expected_role
        self.assertEqual("deploy", expected_role("main.py"))
        self.assertEqual("deploy", expected_role("libs/httplib2/__init__.py"))
        self.assertEqual("deploy", expected_role("oauth2client/appengine.py"))
        self.assertEqual("test", expected_role("tests/test_rules.py"))
        self.assertEqual("test", expected_role("libs/bs4/tests/test_docs.py"))
        self.assertEqual("tool", expected_role("scripts/check-configured-user-id.py"))

    def test_worktree_surface_excludes_git_ignored_python_files(self):
        repository = tempfile.mkdtemp(prefix="email-python-surface-")
        try:
            subprocess.check_call(["git", "init", "--quiet"], cwd=repository)
            with open(os.path.join(repository, ".gitignore"), "w") as ignore_file:
                ignore_file.write("env/\n")
            with open(os.path.join(repository, "tracked.py"), "w") as tracked_file:
                tracked_file.write("tracked = True\n")
            subprocess.check_call(["git", "add", ".gitignore", "tracked.py"], cwd=repository)
            os.mkdir(os.path.join(repository, "env"))
            with open(os.path.join(repository, "env", "local.py"), "w") as ignored_file:
                ignored_file.write("ignored = True\n")
            with open(os.path.join(repository, "untracked.py"), "w") as untracked_file:
                untracked_file.write("untracked = True\n")

            self.assertEqual(
                set(["tracked.py", "untracked.py"]),
                AUTHORITY.worktree_python(repository),
            )
        finally:
            shutil.rmtree(repository)

    def test_complete_tracked_surface_matches_interpreter_contract(self):
        python2 = os.environ.get("PYTHON2", "python2")
        python3 = os.environ.get("PYTHON3", "python3")
        if sys.version_info[0] == 2:
            python2 = sys.executable
        else:
            python3 = sys.executable
        command = [
            sys.executable,
            os.path.join(ROOT_DIR, "scripts", "verify-python-surface.py"),
            ROOT_DIR,
            os.path.join(ROOT_DIR, "scripts", "python-surface-scopes.txt"),
            python2,
            python3,
        ]
        self.assertEqual(0, subprocess.call(command))

    def test_python314_accepts_incidental_compatibility(self):
        python314 = os.environ.get("PYTHON314", "python3.14")
        if not self.executable_available(python314):
            self.skipTest("supplemental Python 3.14 is not available")
        command = [
            sys.executable,
            os.path.join(ROOT_DIR, "scripts", "verify-python-surface.py"),
            ROOT_DIR,
            os.path.join(ROOT_DIR, "scripts", "python-surface-scopes.txt"),
            "-",
            python314,
        ]
        self.assertEqual(0, subprocess.call(command))

    def test_missing_supplemental_runtime_keeps_selected_runtime_authoritative(self):
        python2 = sys.executable if sys.version_info[0] == 2 else "-"
        python3 = sys.executable if sys.version_info[0] == 3 else "-"
        command = [
            sys.executable,
            os.path.join(ROOT_DIR, "scripts", "verify-python-surface.py"),
            ROOT_DIR,
            os.path.join(ROOT_DIR, "scripts", "python-surface-scopes.txt"),
            python2,
            python3,
        ]
        environment = os.environ.copy()
        environment["PYTHON314"] = ""
        self.assertEqual(0, subprocess.call(command, env=environment))


if __name__ == "__main__":
    unittest.main()
