from kakeibo_exporter import __version__


# TODO: SmallテストとMediumテストを分ける
#       参考：https://testing.googleblog.com/2010/12/test-sizes.html
#       pytest のMarking：https://docs.pytest.org/en/latest/example/markers.html
def test_version():
    assert __version__ == "0.1.0"
