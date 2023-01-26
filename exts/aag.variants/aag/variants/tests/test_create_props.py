# NOTE:
#   omni.kit.test - std python's unittest module with additional wrapping to add suport for async/await tests
#   For most things refer to unittest docs: https://docs.python.org/3/library/unittest.html
import omni.kit.test

# Extnsion for writing UI tests (simulate UI interaction)
import omni.kit.ui_test as ui_test

# Import extension python module we are testing with absolute import path, as if we are external user (other extension)
from aag.variants.src import CreatePropsFrom3DSmax


# Having a test class dervived from omni.kit.test.AsyncTestCase declared on the root of module will make it auto-discoverable by omni.kit.test
class Test(omni.kit.test.AsyncTestCase):

    # Before running each test
    async def setUp(self):
        pass

    # After running each test
    async def tearDown(self):
        pass

    async def test_get_prop_list_from_path_source_empty(self):
        """
        GIVEN Empty source folder
        WHEN get_prop_list_from_path is called
        THEN it returns an empty list of strings
        """

        