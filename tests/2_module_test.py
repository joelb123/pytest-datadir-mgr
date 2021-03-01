# -*- coding: utf-8 -*-
"""Tests at module scope."""
# standard library imports
from pathlib import Path

# third-party imports
import pytest

# module imports
from . import DLFILE
from . import NEWPATH
from . import TESTFILE

NEWMSG = "data saved from test_in_tmp_dir\n"
LOGPATH = Path("test_in_tmp_dir.log")
BSD3 = (Path(__file__).parent.parent / DLFILE).open("r").read()
REPO_URL = "https://raw.githubusercontent.com/joelb123/pytest-datadir-mgr/main/"


def test_function_scope(datadir_mgr):
    """Test function scope."""
    data1_path = datadir_mgr[TESTFILE]
    with open(data1_path, "r") as filehandle:
        contents = filehandle.read()
        assert contents == "data at function scope\n"


def test_download(datadir_mgr):
    """Test simple download."""
    datadir_mgr.download(
        REPO_URL, files=[DLFILE], scope="module", progressbar=True
    )
    with datadir_mgr[DLFILE].open("r") as dlfilehandle:
        license_txt = dlfilehandle.read()
    assert license_txt == BSD3


def test_gzipped_download(datadir_mgr):
    """Test download of gzipped file."""
    datadir_mgr.download(
        REPO_URL + "tests/dltest",
        files=[DLFILE],
        scope="function",
        gunzip=True,
    )
    with datadir_mgr[DLFILE].open("r") as dlfilehandle:
        license_txt = dlfilehandle.read()
    assert license_txt == BSD3


def test_download_with_md5sum(datadir_mgr):
    """Test download of gzipped file with MD5 check."""
    datadir_mgr.download(
        REPO_URL + "tests/dltest/",
        files=[DLFILE],
        scope="function",
        gunzip=True,
        md5_check=True,
    )
    with datadir_mgr[DLFILE].open("r") as dlfilehandle:
        license_txt = dlfilehandle.read()
    assert license_txt == BSD3


def test_saved_data(datadir_mgr):
    """Test reading data from previous context."""
    datadir_mgr.add_scope(
        "saved data", module="1_global_test", func="test_savepath"
    )
    data1_path = datadir_mgr[TESTFILE]
    with open(data1_path, "r") as filehandle:
        contents = filehandle.read()
        assert contents == "data saved from test_savepath\n"


def test_empty_tmp_dir(datadir_mgr):
    """Test using context manager with no data."""
    with datadir_mgr.in_tmp_dir():
        NEWPATH.parent.mkdir(parents=True, exist_ok=True)
        with NEWPATH.open("w") as filehandle:
            filehandle.write(NEWMSG)


def test_in_tmp_dir(datadir_mgr, capsys):
    """Test using context manager with saved data."""
    with capsys.disabled():
        with datadir_mgr.in_tmp_dir(
            inpathlist=[DLFILE, TESTFILE],
            save_outputs=True,
            outscope="function",
            excludepatterns=["*.log"],
            progressbar=True,
        ):
            data1 = open(datadir_mgr[TESTFILE]).read()
            dlpath = Path(DLFILE)
            assert data1 == "data at module scope\n"
            assert dlpath.exists()
            NEWPATH.parent.mkdir(parents=True, exist_ok=True)
            with NEWPATH.open("w") as filehandle:
                filehandle.write(NEWMSG)
            with LOGPATH.open("w") as logfilehandle:
                logfilehandle.write("here is a log file")
    assert not dlpath.exists()


def test_autosaved_data(datadir_mgr):
    """Test using autosaved data."""
    datadir_mgr.add_scope(
        "autosaved data", module="2_module_test", func="test_in_tmp_dir"
    )
    with pytest.raises(KeyError):  # better not find the log file
        datadir_mgr[LOGPATH]  # NOQA
    with datadir_mgr.in_tmp_dir(inpathlist=[NEWPATH]):
        hellomsg = NEWPATH.open().read()
        assert hellomsg == NEWMSG
