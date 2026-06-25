from __future__ import print_function

import os
import shutil
import subprocess
import sys
import tempfile


ROOT = os.environ.get(
    "PYTHON_SURFACE_ROOT_UNDER_TEST",
    os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
)
PYTHON2 = os.environ.get("PYTHON2", "python2")
PYTHON3 = os.environ.get("PYTHON3", "python3")
PYTHON310 = os.environ.get("PYTHON310", "python3.10")
PYTHON312 = os.environ.get("PYTHON312", "python3.12")
PYTHON314 = os.environ.get("PYTHON314", "python3.14")
PYPY2 = os.environ.get("PYPY2", "pypy2")


def available(executable):
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


RUNNER = PYTHON3 if available(PYTHON3) else PYTHON2


def authority_command(root):
    return [
        RUNNER,
        os.path.join(root, "scripts", "verify-python-surface.py"),
        root,
        os.path.join(root, "scripts", "python-surface-scopes.txt"),
        PYTHON2,
        PYTHON3,
    ]


def run(root, expect_success=False, command=None):
    result = subprocess.call(
        command or authority_command(root),
        cwd=root,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
    )
    if (result == 0) != expect_success:
        raise SystemExit("unexpected mutation result: %r returned %d" % (
            command or authority_command(root), result,
        ))


def clone_case(name):
    destination = os.path.join(TEMP_DIR, name)
    os.mkdir(destination)
    output = subprocess.check_output([
        "git", "ls-files", "-z", "--cached", "--others", "--exclude-standard",
    ], cwd=ROOT)
    if not isinstance(output, str):
        output = output.decode("utf-8")
    for relative in output.split("\0"):
        if not relative:
            continue
        source = os.path.join(ROOT, relative)
        target = os.path.join(destination, relative)
        parent = os.path.dirname(target)
        if not os.path.isdir(parent):
            os.makedirs(parent)
        if os.path.islink(source):
            os.symlink(os.readlink(source), target)
        else:
            shutil.copy2(source, target)
    subprocess.check_call(["git", "init", "--quiet", destination])
    subprocess.check_call(["git", "-C", destination, "add", "."])
    return destination


def scope_path(root):
    return os.path.join(root, "scripts", "python-surface-scopes.txt")


def replace(root, relative_path, old, new):
    path = os.path.join(root, relative_path)
    with open(path, "r") as source_file:
        content = source_file.read()
    if old not in content:
        raise SystemExit("mutation marker missing: %s" % old)
    with open(path, "w") as source_file:
        source_file.write(content.replace(old, new, 1))


def append_scope(root, record):
    with open(scope_path(root), "a") as scope_file:
        scope_file.write(record + "\n")


def populate_isolated_path(destination):
    os.mkdir(destination)
    for source_dir in ("/bin", "/usr/bin"):
        for name in os.listdir(source_dir):
            if name.startswith("python") or name.startswith("pypy"):
                continue
            source = os.path.join(source_dir, name)
            target = os.path.join(destination, name)
            if os.path.exists(target) or not os.access(source, os.X_OK):
                continue
            os.symlink(source, target)


def runtime_path(executable):
    if os.path.isabs(executable):
        return os.path.realpath(executable)
    for directory in os.environ.get("PATH", "").split(os.pathsep):
        candidate = os.path.join(directory, executable)
        if os.path.isfile(candidate) and os.access(candidate, os.X_OK):
            return os.path.realpath(candidate)
    raise SystemExit("runtime path is unavailable: %s" % executable)


def link_runtime(destination, executable, names):
    for name in names:
        os.symlink(runtime_path(executable), os.path.join(destination, name))


def isolated_runtime_check(name, python2, python3, python314="", full_make=True):
    case = clone_case(name)
    isolated_bin = os.path.join(TEMP_DIR, name + "-bin")
    populate_isolated_path(isolated_bin)
    selected = python3 if available(python3) else python2
    if available(python2):
        link_runtime(isolated_bin, python2, ("python2", "pypy2"))
    if available(python3):
        link_runtime(isolated_bin, python3, ("python3",))
    link_runtime(isolated_bin, selected, ("python",))
    environment = os.environ.copy()
    for variable in ("MAKEFLAGS", "MFLAGS", "MAKEOVERRIDES", "GNUMAKEFLAGS", "MAKEFILES"):
        environment.pop(variable, None)
    environment.update({
        "PATH": isolated_bin,
        "PYTHON": "python",
        "PYTHON2": "python2" if available(python2) else "-",
        "PYTHON3": "python3" if available(python3) else "-",
        "PYTHON314": python314,
        "SKIP_PYTHON_SURFACE_MUTATIONS": "1",
    })
    commands = [["make", "--no-print-directory", "check"]]
    if not full_make:
        commands = [
            ["python", os.path.join(case, "tests", "test_cache.py")],
            ["python", os.path.join(case, "tests", "test_python_surface_authority.py")],
            [
                "python",
                os.path.join(case, "scripts", "verify-python-surface.py"),
                case,
                os.path.join(case, "scripts", "python-surface-scopes.txt"),
                "python2",
                "-",
            ],
        ]
    for command in commands:
        process = subprocess.Popen(
            command,
            cwd=case,
            env=environment,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            if not isinstance(stdout, str):
                stdout = stdout.decode("utf-8", "replace")
            if not isinstance(stderr, str):
                stderr = stderr.decode("utf-8", "replace")
            raise SystemExit("isolated runtime check failed: %s returned %d\n%s%s" % (
                name, process.returncode, stdout, stderr,
            ))


TEMP_DIR = tempfile.mkdtemp(prefix="email-automator-python-surface.")
try:
    ignored_probe = os.path.join(ROOT, "build", "python-surface-ignored-probe.py")
    ignored_parent_created = not os.path.isdir(os.path.dirname(ignored_probe))
    if ignored_parent_created:
        os.makedirs(os.path.dirname(ignored_probe))
    with open(ignored_probe, "w") as probe_file:
        probe_file.write("ignored = True\n")
    try:
        ignored_case = clone_case("ignored-local-files")
        if os.path.exists(os.path.join(ignored_case, "build", "python-surface-ignored-probe.py")):
            raise SystemExit("ignored local Python file was copied into mutation case")
    finally:
        os.unlink(ignored_probe)
        if ignored_parent_created:
            os.rmdir(os.path.dirname(ignored_probe))

    run(ROOT, expect_success=True)
    if available(PYTHON314):
        run(ROOT, expect_success=True, command=[
            PYTHON3,
            os.path.join(ROOT, "scripts", "verify-python-surface.py"),
            ROOT,
            os.path.join(ROOT, "scripts", "python-surface-scopes.txt"),
            "-",
            PYTHON314,
        ])

    for version, executable in (
        ("python310-only", PYTHON310),
        ("python312-only", PYTHON312),
        ("python314-only", PYTHON314),
    ):
        if available(executable):
            isolated_runtime_check(version, "-", executable)
    if available(PYPY2):
        isolated_runtime_check("pypy2-only", PYPY2, "-", full_make=False)
    if available(PYPY2) and available(PYTHON3):
        supplemental = PYTHON314 if available(PYTHON314) and PYTHON314 != PYTHON3 else ""
        isolated_runtime_check("multi-runtime", PYPY2, PYTHON3, supplemental)

    corruptions = [("corrupt-oauth2client", "oauth2client/appengine.py")]
    if available(PYTHON2):
        corruptions.append(("corrupt-httplib2", "libs/httplib2/__init__.py"))
    for name, target in corruptions:
        case = clone_case(name)
        with open(os.path.join(case, target), "a") as source:
            source.write("\ndef broken(:\n")
        run(case)

    case = clone_case("omitted-scope")
    replace(case, "scripts/python-surface-scopes.txt", "both deploy oauth2client/appengine.py\n", "")
    run(case)

    case = clone_case("tracked-new-module")
    with open(os.path.join(case, "oauth2client", "new_runtime.py"), "w") as source:
        source.write("value = 1\n")
    subprocess.check_call(["git", "-C", case, "add", "oauth2client/new_runtime.py"])
    run(case)

    case = clone_case("untracked-new-module")
    with open(os.path.join(case, "oauth2client", "untracked_runtime.py"), "w") as source:
        source.write("value = 1\n")
    run(case)

    case = clone_case("generated-bytecode-excluded")
    generated = os.path.join(case, "oauth2client", "__pycache__")
    os.mkdir(generated)
    with open(os.path.join(generated, "generated.pyc"), "wb") as bytecode:
        bytecode.write(b"not real bytecode")
    run(case, expect_success=True)

    case = clone_case("extra-untracked-scope")
    append_scope(case, "both deploy oauth2client/not-present.py")
    run(case)

    case = clone_case("path-traversal")
    append_scope(case, "both deploy ../escape.py")
    run(case)

    case = clone_case("absolute-path")
    append_scope(case, "both deploy /tmp/escape.py")
    run(case)

    case = clone_case("canonical-duplicate")
    append_scope(case, "both deploy oauth2client/./appengine.py")
    run(case)

    case = clone_case("wrong-family")
    replace(
        case,
        "scripts/python-surface-scopes.txt",
        "both deploy oauth2client/appengine.py",
        "python3 deploy oauth2client/appengine.py",
    )
    run(case)

    case = clone_case("wrong-role-boundary")
    replace(
        case,
        "scripts/python-surface-scopes.txt",
        "both test tests/test_rules.py",
        "both deploy tests/test_rules.py",
    )
    run(case)

    case = clone_case("wrong-vendored-test-boundary")
    replace(
        case,
        "scripts/python-surface-scopes.txt",
        "both test libs/bs4/tests/test_docs.py",
        "both deploy libs/bs4/tests/test_docs.py",
    )
    run(case)

    case = clone_case("symlink-worktree")
    os.unlink(os.path.join(case, "oauth2client", "appengine.py"))
    os.symlink("../main.py", os.path.join(case, "oauth2client", "appengine.py"))
    run(case)

    case = clone_case("index-only")
    path = os.path.join(case, "oauth2client", "index_only.py")
    with open(path, "w") as source:
        source.write("value = 1\n")
    subprocess.check_call(["git", "-C", case, "add", "oauth2client/index_only.py"])
    os.unlink(path)
    run(case)

    case = clone_case("compile-loop-disabled")
    replace(
        case,
        "scripts/verify-python-surface.py",
        "return subprocess.call(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0",
        "return True",
    )
    with open(os.path.join(case, "oauth2client", "appengine.py"), "a") as source:
        source.write("\ndef broken(:\n")
    run(case, command=[
        "env",
        "SKIP_PYTHON_SURFACE_MUTATIONS=1",
        "make",
        "--no-print-directory",
        "check",
    ])

    case = clone_case("make-build-disabled")
    replace(
        case,
        "Makefile",
        '$(PYTHON) "$(ROOT)/scripts/verify-python-surface.py"',
        '@true # $(PYTHON) "$(ROOT)/scripts/verify-python-surface.py"',
    )
    run(case, command=[
        "env",
        "SKIP_PYTHON_SURFACE_MUTATIONS=1",
        "make",
        "--no-print-directory",
        "check",
    ])

    print("Complete Python surface mutations passed.")
finally:
    shutil.rmtree(TEMP_DIR)
