from __future__ import print_function

import os
import stat
import subprocess
import sys
import tempfile


FAMILIES = ("both", "python2", "python3")
ROLES = ("deploy", "test", "tool")
REGULAR_MODES = ("100644", "100755")


def command_output(command, cwd):
    output = subprocess.check_output(command, cwd=cwd)
    if not isinstance(output, str):
        output = output.decode("utf-8")
    return output


def indexed_python(root):
    output = command_output(["git", "ls-files", "-s", "-z", "--", "*.py"], root)
    records = {}
    for raw_record in output.split("\0"):
        if not raw_record:
            continue
        metadata, path = raw_record.split("\t", 1)
        mode, unused_object, stage = metadata.split()
        if stage != "0" or mode not in REGULAR_MODES:
            raise SystemExit("Indexed Python path is not a regular stage-zero file: %s" % path)
        records[path] = mode
    return records


def worktree_python(root):
    paths = set()
    root_real = os.path.realpath(root)
    for directory, names, filenames in os.walk(root):
        names[:] = [name for name in names if name != ".git"]
        for filename in filenames:
            if not filename.endswith(".py"):
                continue
            absolute = os.path.join(directory, filename)
            relative = os.path.relpath(absolute, root)
            file_mode = os.lstat(absolute).st_mode
            if not stat.S_ISREG(file_mode):
                raise SystemExit("Worktree Python path is not a regular file: %s" % relative)
            target = os.path.realpath(absolute)
            if target != root_real and not target.startswith(root_real + os.sep):
                raise SystemExit("Worktree Python path escapes repository: %s" % relative)
            paths.add(relative)
    return paths


def expected_role(path):
    if path == "test.py" or path.startswith("tests/") or path.startswith("libs/bs4/tests/"):
        return "test"
    if path.startswith("scripts/"):
        return "tool"
    return "deploy"


def load_scopes(root, scope_path):
    root_real = os.path.realpath(root)
    records = {}
    canonical = {}
    with open(scope_path, "r") as scope_file:
        for number, raw_line in enumerate(scope_file, 1):
            line = raw_line.rstrip("\r\n")
            fields = line.split()
            if len(fields) != 3:
                raise SystemExit("Invalid scope record on line %d." % number)
            family, role, path = fields
            if family not in FAMILIES or role not in ROLES:
                raise SystemExit("Unknown family or role on line %d." % number)
            if os.path.isabs(path) or path != os.path.normpath(path) or path.startswith(".." + os.sep):
                raise SystemExit("Non-canonical scope path: %s" % path)
            target = os.path.realpath(os.path.join(root_real, path))
            if target != root_real and not target.startswith(root_real + os.sep):
                raise SystemExit("Scope path escapes repository: %s" % path)
            if path in records:
                raise SystemExit("Duplicate scope path: %s" % path)
            if target in canonical:
                raise SystemExit("Canonical duplicate: %s and %s" % (canonical[target], path))
            records[path] = (family, role)
            canonical[target] = path
    return records


def available(interpreter):
    if not interpreter or interpreter == "-":
        return False
    try:
        return subprocess.call(
            [interpreter, "-c", "import sys"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        ) == 0
    except OSError:
        return False


def supports(interpreter, path, cfile):
    command = [
        interpreter,
        "-c",
        "import py_compile,sys; py_compile.compile(sys.argv[1], cfile=sys.argv[2], doraise=True)",
        path,
        cfile,
    ]
    return subprocess.call(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE) == 0


def main(root, scope_path, python2, python3):
    indexed = indexed_python(root)
    worktree = worktree_python(root)
    indexed_paths = set(indexed)
    if indexed_paths != worktree:
        raise SystemExit("Index/worktree Python mismatch; index_only=%r worktree_only=%r" % (
            sorted(indexed_paths - worktree), sorted(worktree - indexed_paths),
        ))

    records = load_scopes(root, scope_path)
    declared = set(records)
    if declared != indexed_paths:
        raise SystemExit("Scope coverage mismatch; missing=%r extra=%r" % (
            sorted(indexed_paths - declared), sorted(declared - indexed_paths),
        ))

    for path, record in records.items():
        family, role = record
        if role != expected_role(path):
            raise SystemExit("Wrong role for %s: %s" % (path, role))
        if role == "deploy" and family == "python3":
            raise SystemExit("Deployed Python path lacks Python 2 support: %s" % path)

    interpreters = (("python2", python2), ("python3", python3))
    active = [(family, executable) for family, executable in interpreters if available(executable)]
    if not active:
        raise SystemExit("No Python interpreter is available for compile verification.")

    temp_dir = tempfile.mkdtemp(prefix="email-automator-pyc.")
    try:
        for index, path in enumerate(sorted(indexed_paths)):
            expected_family = records[path][0]
            required = set(FAMILIES[1:] if expected_family == "both" else (expected_family,))
            for family, executable in active:
                if family not in required:
                    continue
                cfile = os.path.join(temp_dir, "%s-%d.pyc" % (family, index))
                compiled = supports(executable, os.path.join(root, path), cfile)
                if not compiled:
                    raise SystemExit("Interpreter scope mismatch for %s under %s." % (path, family))
    finally:
        for filename in os.listdir(temp_dir):
            os.unlink(os.path.join(temp_dir, filename))
        os.rmdir(temp_dir)

    deployed = sum(1 for family, role in records.values() if role == "deploy")
    print("Verified %d tracked Python files, including %d deployed files." % (
        len(indexed_paths), deployed,
    ))


if __name__ == "__main__":
    if len(sys.argv) != 5:
        raise SystemExit("usage: verify-python-surface.py ROOT SCOPES PYTHON2 PYTHON3")
    main(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4])
